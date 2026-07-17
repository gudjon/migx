/* Core Audio HAL soak — measurement only (Wave 1 / PS-PLT-01).
 *
 * Pure AudioUnit output (no PortAudio / JACK). Counts render-callback
 * under-runs via kAudioUnitErr_CannotDoInCurrentContext style flags is not
 * exposed the same way as PA; we measure:
 *   - successful open of default output
 *   - callback period p50/p99/max vs expected buffer period
 *   - late callbacks (period > 1.5× expected) as soft-xrun proxies
 *   - zero hard failures during open/start/stop
 *
 * Build:
 *   clang -O2 -std=c11 tools/soundio/coreaudio_pa_soak.c \
 *     -framework AudioUnit -framework AudioToolbox -framework CoreAudio \
 *     -framework CoreFoundation -o tools/soundio/coreaudio_pa_soak
 */
#include <AudioToolbox/AudioToolbox.h>
#include <CoreAudio/CoreAudio.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

typedef struct {
    double phase;
    double freq;
    double sample_rate;
    UInt32 channels;
    unsigned long callbacks;
    unsigned long late; /* period > 1.5× expected */
    unsigned long hard_err;
    double expected_ms;
    double last_cb_mono;
    double* periods_ms;
    size_t periods_cap;
    size_t periods_len;
} SoakState;

static double mono_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1000.0 + (double)ts.tv_nsec / 1.0e6;
}

static int cmp_double(const void* a, const void* b) {
    double da = *(const double*)a;
    double db = *(const double*)b;
    return (da > db) - (da < db);
}

static double percentile(double* sorted, size_t n, double p) {
    if (n == 0) {
        return 0.0;
    }
    double idx = p * (double)(n - 1);
    size_t lo = (size_t)idx;
    size_t hi = lo + 1 < n ? lo + 1 : lo;
    double t = idx - (double)lo;
    return sorted[lo] * (1.0 - t) + sorted[hi] * t;
}

static OSStatus render_cb(void* inRefCon,
        AudioUnitRenderActionFlags* ioActionFlags,
        const AudioTimeStamp* inTimeStamp,
        UInt32 inBusNumber,
        UInt32 inNumberFrames,
        AudioBufferList* ioData) {
    (void)ioActionFlags;
    (void)inTimeStamp;
    (void)inBusNumber;
    SoakState* s = (SoakState*)inRefCon;
    const double now = mono_ms();

    if (s->callbacks > 0 && s->periods_len < s->periods_cap) {
        double period = now - s->last_cb_mono;
        s->periods_ms[s->periods_len++] = period;
        if (period > s->expected_ms * 1.5) {
            s->late++;
        }
    }
    s->last_cb_mono = now;
    s->callbacks++;

    if (!ioData) {
        s->hard_err++;
        return noErr;
    }

    const double two_pi = 6.283185307179586;
    for (UInt32 b = 0; b < ioData->mNumberBuffers; ++b) {
        float* out = (float*)ioData->mBuffers[b].mData;
        if (!out) {
            s->hard_err++;
            continue;
        }
        UInt32 ch = ioData->mBuffers[b].mNumberChannels;
        for (UInt32 i = 0; i < inNumberFrames; ++i) {
            float sample = (float)(0.08 * sin(s->phase));
            s->phase += two_pi * s->freq / s->sample_rate;
            if (s->phase > two_pi) {
                s->phase -= two_pi;
            }
            for (UInt32 c = 0; c < ch; ++c) {
                out[i * ch + c] = sample;
            }
        }
    }
    return noErr;
}

static void list_devices(void) {
    AudioObjectPropertyAddress addr = {
            kAudioHardwarePropertyDevices,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMain};
    UInt32 size = 0;
    OSStatus st = AudioObjectGetPropertyDataSize(
            kAudioObjectSystemObject, &addr, 0, NULL, &size);
    if (st != noErr) {
        fprintf(stderr, "list size err %d\n", (int)st);
        return;
    }
    UInt32 count = size / sizeof(AudioDeviceID);
    AudioDeviceID* devs = (AudioDeviceID*)malloc(size);
    st = AudioObjectGetPropertyData(
            kAudioObjectSystemObject, &addr, 0, NULL, &size, devs);
    if (st != noErr) {
        free(devs);
        return;
    }
    printf("device_count=%u\n", count);
    for (UInt32 i = 0; i < count; ++i) {
        char name[256] = {0};
        UInt32 nsize = sizeof(name);
        AudioObjectPropertyAddress naddr = {
                kAudioDevicePropertyDeviceNameCFString,
                kAudioObjectPropertyScopeGlobal,
                kAudioObjectPropertyElementMain};
        CFStringRef cfname = NULL;
        UInt32 cfsz = sizeof(cfname);
        if (AudioObjectGetPropertyData(devs[i], &naddr, 0, NULL, &cfsz, &cfname) ==
                        noErr &&
                cfname) {
            CFStringGetCString(cfname, name, sizeof(name), kCFStringEncodingUTF8);
            CFRelease(cfname);
        }
        printf("device[%u] id=%u name=\"%s\"\n", i, (unsigned)devs[i], name);
    }
    free(devs);

    AudioDeviceID def = kAudioObjectUnknown;
    UInt32 dsz = sizeof(def);
    AudioObjectPropertyAddress daddr = {
            kAudioHardwarePropertyDefaultOutputDevice,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMain};
    if (AudioObjectGetPropertyData(
                kAudioObjectSystemObject, &daddr, 0, NULL, &dsz, &def) == noErr) {
        printf("default_output_id=%u\n", (unsigned)def);
    }
}

static void usage(const char* a0) {
    fprintf(stderr,
            "Usage: %s [--seconds N] [--buffer FRAMES] [--rate HZ] [--list]\n",
            a0);
}

int main(int argc, char** argv) {
    int seconds = 30;
    UInt32 buffer_frames = 256;
    double sample_rate = 48000.0;
    int list_only = 0;

    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--seconds") && i + 1 < argc) {
            seconds = atoi(argv[++i]);
        } else if (!strcmp(argv[i], "--buffer") && i + 1 < argc) {
            buffer_frames = (UInt32)atoi(argv[++i]);
        } else if (!strcmp(argv[i], "--rate") && i + 1 < argc) {
            sample_rate = atof(argv[++i]);
        } else if (!strcmp(argv[i], "--list")) {
            list_only = 1;
        } else if (!strcmp(argv[i], "--help")) {
            usage(argv[0]);
            return 0;
        } else {
            usage(argv[0]);
            return 2;
        }
    }

    list_devices();
    if (list_only) {
        return 0;
    }

    AudioComponentDescription desc = {
            .componentType = kAudioUnitType_Output,
            .componentSubType = kAudioUnitSubType_DefaultOutput,
            .componentManufacturer = kAudioUnitManufacturer_Apple,
    };
    AudioComponent comp = AudioComponentFindNext(NULL, &desc);
    if (!comp) {
        fprintf(stderr, "no DefaultOutput AudioUnit\n");
        return 1;
    }
    AudioUnit unit = NULL;
    OSStatus st = AudioComponentInstanceNew(comp, &unit);
    if (st != noErr) {
        fprintf(stderr, "AudioComponentInstanceNew %d\n", (int)st);
        return 1;
    }

    AudioStreamBasicDescription asbd = {0};
    asbd.mSampleRate = sample_rate;
    asbd.mFormatID = kAudioFormatLinearPCM;
    asbd.mFormatFlags = kAudioFormatFlagIsFloat | kAudioFormatFlagIsPacked |
            kAudioFormatFlagsNativeEndian;
    asbd.mFramesPerPacket = 1;
    asbd.mChannelsPerFrame = 2;
    asbd.mBitsPerChannel = 32;
    asbd.mBytesPerFrame = 8;
    asbd.mBytesPerPacket = 8;

    st = AudioUnitSetProperty(unit,
            kAudioUnitProperty_StreamFormat,
            kAudioUnitScope_Input,
            0,
            &asbd,
            sizeof(asbd));
    if (st != noErr) {
        fprintf(stderr, "set format %d\n", (int)st);
        AudioComponentInstanceDispose(unit);
        return 1;
    }

    st = AudioUnitSetProperty(unit,
            kAudioDevicePropertyBufferFrameSize,
            kAudioUnitScope_Global,
            0,
            &buffer_frames,
            sizeof(buffer_frames));
    /* buffer size set may fail on some devices — continue with device default */

    SoakState state;
    memset(&state, 0, sizeof(state));
    state.freq = 440.0;
    state.sample_rate = sample_rate;
    state.channels = 2;
    state.expected_ms = 1000.0 * (double)buffer_frames / sample_rate;
    state.periods_cap = (size_t)(seconds * 2000);
    if (state.periods_cap < 2048) {
        state.periods_cap = 2048;
    }
    state.periods_ms = (double*)calloc(state.periods_cap, sizeof(double));
    if (!state.periods_ms) {
        AudioComponentInstanceDispose(unit);
        return 1;
    }

    AURenderCallbackStruct cb = {.inputProc = render_cb, .inputProcRefCon = &state};
    st = AudioUnitSetProperty(unit,
            kAudioUnitProperty_SetRenderCallback,
            kAudioUnitScope_Input,
            0,
            &cb,
            sizeof(cb));
    if (st != noErr) {
        fprintf(stderr, "set callback %d\n", (int)st);
        free(state.periods_ms);
        AudioComponentInstanceDispose(unit);
        return 1;
    }

    st = AudioUnitInitialize(unit);
    if (st != noErr) {
        fprintf(stderr, "AudioUnitInitialize %d\n", (int)st);
        free(state.periods_ms);
        AudioComponentInstanceDispose(unit);
        return 1;
    }

    /* Read back actual buffer size */
    UInt32 actual_buf = buffer_frames;
    UInt32 absz = sizeof(actual_buf);
    AudioUnitGetProperty(unit,
            kAudioDevicePropertyBufferFrameSize,
            kAudioUnitScope_Global,
            0,
            &actual_buf,
            &absz);
    state.expected_ms = 1000.0 * (double)actual_buf / sample_rate;

    printf("soak rate=%.0f buffer_req=%u buffer_actual=%u expected_ms=%.3f seconds=%d\n",
            sample_rate,
            buffer_frames,
            actual_buf,
            state.expected_ms,
            seconds);

    state.last_cb_mono = mono_ms();
    st = AudioOutputUnitStart(unit);
    if (st != noErr) {
        fprintf(stderr, "AudioOutputUnitStart %d\n", (int)st);
        free(state.periods_ms);
        AudioComponentInstanceDispose(unit);
        return 1;
    }

    sleep((unsigned)seconds);

    st = AudioOutputUnitStop(unit);
    if (st != noErr) {
        fprintf(stderr, "AudioOutputUnitStop %d\n", (int)st);
        state.hard_err++;
    }
    AudioUnitUninitialize(unit);
    AudioComponentInstanceDispose(unit);

    qsort(state.periods_ms, state.periods_len, sizeof(double), cmp_double);
    double p50 = percentile(state.periods_ms, state.periods_len, 0.50);
    double p99 = percentile(state.periods_ms, state.periods_len, 0.99);
    double pmax = state.periods_len ? state.periods_ms[state.periods_len - 1] : 0.0;
    double pmin = state.periods_len ? state.periods_ms[0] : 0.0;

    /* Gate: no hard errors, callbacks fired, late ratio < 0.1% for short soaks
     * (late is soft proxy; Migxx PA underrun is separate — dual-deck GUI soak). */
    int pass = state.hard_err == 0 && state.callbacks > 10 &&
            state.late * 1000 < state.callbacks; /* <0.1% late */

    printf("RESULT callbacks=%lu late=%lu hard_err=%lu\n",
            state.callbacks,
            state.late,
            state.hard_err);
    printf("RESULT period_ms expected=%.3f min=%.3f p50=%.3f p99=%.3f max=%.3f n=%zu\n",
            state.expected_ms,
            pmin,
            p50,
            p99,
            pmax,
            state.periods_len);
    printf("RESULT gate_stable_callback=%s\n", pass ? "PASS" : "FAIL");

    free(state.periods_ms);
    return pass ? 0 : 3;
}

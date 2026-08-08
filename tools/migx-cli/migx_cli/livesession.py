"""Two decks and a running order that can still change — the live session.

**ORPHAN (2026-08-08): nothing in the repo imports this.** It has only ever run
from a throwaway driver in a scratchpad, which is how it played a real set —
and why that capability does not survive the shell that ran it.

The missing piece is a driver: `tick()` must be called repeatedly, and the TUI
redraw loop is its natural home (one `tick()` per frame, `state()` into the Deck
pane). Until then this is tested, correct and unreachable — the same
"inventory" the rest of this codebase spent a day eliminating, and it is called
out here rather than left for a future reader to discover with grep.

Steps 3-5 of the TUI path: a second deck so blends overlap, transport so a DJ
can act, and a re-plan after every track so tonight's feedback changes tonight's
set.

## What makes this different from a rendered mix

`setplay` decides all 25 transitions before the first note. Here, only the NEXT
track is ever committed, and it is chosen from the *current* pool at the moment
the outgoing track approaches its exit. Say "retire this" at 1am and the very
next selection already reflects it.

## The blend is scheduled, not ridden

Both decks are external player processes; we cannot move a fader. So the
incoming deck is launched with its tempo and fade-in baked in at the moment the
overlap should begin. That is a real, audible, beatmatched blend — and it is
NOT hand mixing. The TUI must not draw a crossfader it cannot move.

## Why the outgoing deck is not stopped early

It runs to its natural end under the incoming track. Cutting it at the fade
midpoint would be tidier to model and would audibly truncate a record — the
DJ's exit cue, if they set one, already says where the useful part ends.
"""

from __future__ import annotations

import time
from typing import Any, Callable

from . import feedback, mixing, onbeat, player, setplan, setplay

# Start the incoming deck this long before the outgoing one ends. A blend
# shorter than this is a cut; longer and a 3-minute track has no solo section.
DEFAULT_BLEND_S = 12.0

# Below this, do not attempt a blend at all — start the next track cleanly.
MIN_SOLO_S = 20.0


class LiveSession:
    """Two decks, a pool, and the next choice made as late as possible."""

    def __init__(
        self,
        pool: list[dict[str, Any]],
        blend_s: float = DEFAULT_BLEND_S,
        on_event: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        self.decks = (player.Deck(), player.Deck())
        self.active = 0
        self.pool = list(pool)
        self.played: list[dict[str, Any]] = []
        self.blend_s = blend_s
        self._on_event = on_event

    # -- selection ---------------------------------------------------------
    def candidates(self) -> list[dict[str, Any]]:
        """Unplayed, analysed, not retired — re-read every time it is asked.

        Deliberately recomputed rather than cached: `track.feedback` writes to
        the sidecar mid-set, and a cached pool would keep offering a track the
        DJ just retired.
        """
        done = {t.get("path") for t in self.played}
        return [
            t for t in self.pool
            if t.get("path") not in done
            and t.get("bpm") and t.get("camelot")
            and not feedback.is_retired(t)
        ]

    def choose_next(self) -> dict[str, Any] | None:
        """Best next track from what is left, given what is playing now."""
        options = self.candidates()
        if not options:
            return None
        current = self.now_playing()
        if current is None:
            return min(options, key=setplan.opening_energy)
        scored = [(setplan.transition_score(current, c)[0], c) for c in options]
        return max(scored, key=lambda pair: pair[0])[1]

    # -- transport ---------------------------------------------------------
    def now_playing(self) -> dict[str, Any] | None:
        return self.decks[self.active].track

    def state(self) -> dict[str, Any]:
        live = self.decks[self.active].state()
        other = self.decks[1 - self.active].state()
        upcoming = self.choose_next()
        plan = None
        if live.get("name") and upcoming:
            plan = mixing.plan(self.now_playing() or {}, upcoming)
        return {
            "schema": "migx.live-session/1",
            "deck": live,
            "other_deck": other,
            "blending": live["playing"] and other["playing"],
            "played": len(self.played),
            "remaining": len(self.candidates()),
            "next": (upcoming or {}).get("name"),
            "next_move": (plan or {}).get("techniques", [{}])[0].get("name")
            if plan else None,
            "next_pitch_pct": (plan or {}).get("beatmatch", {}).get("pitch_pct")
            if plan else None,
        }

    def _emit(self, name: str) -> None:
        if self._on_event:
            self._on_event(name, self.state())

    def start(self, track: dict[str, Any] | None = None) -> dict[str, Any]:
        chosen = track or self.choose_next()
        if chosen is None:
            return {"ok": False, "error": "nothing playable left"}
        result = self.decks[self.active].play(
            chosen, start_s=setplay.entry_point(chosen)
        )
        if result.get("ok"):
            self.played.append(chosen)
            self._emit("TrackPlaying")
        return result

    def blend_into_next(self, track: dict[str, Any] | None = None) -> dict[str, Any]:
        """Start the next track on the free deck, beatmatched and fading in."""
        incoming = track or self.choose_next()
        if incoming is None:
            return {"ok": False, "error": "nothing playable left"}

        outgoing = self.now_playing()
        ratio, fade = 1.0, self.blend_s
        if outgoing and outgoing.get("bpm") and incoming.get("bpm"):
            beat = mixing.beatmatch(outgoing["bpm"], incoming["bpm"])
            wanted = float(outgoing["bpm"]) / float(incoming["bpm"])
            # Only pitch when a real fader could reach it; otherwise cut in at
            # native tempo rather than warping the record (setplay's rule).
            if not beat.get("relation") and abs(wanted - 1.0) <= setplay.MAX_PITCH:
                ratio = wanted
            else:
                fade = setplay.CUT_CROSSFADE

        # Phase alignment. Tempo matching alone leaves two records running at
        # the same speed with their bars offset — a flam, not a mix. Hold until
        # the OUTGOING track crosses a bar line, then enter the incoming track
        # on one of ITS bar lines, measured at the PLAYED tempo.
        entry = setplay.entry_point(incoming)
        aligned = None
        position = self.decks[self.active].position_s()
        if position is not None and outgoing and outgoing.get("bpm") and incoming.get("bpm"):
            aligned = onbeat.align(
                outgoing_position_s=position,
                outgoing_bpm=float(outgoing["bpm"]),
                incoming_entry_s=entry,
                incoming_bpm=float(incoming["bpm"]),
                tempo_ratio=ratio,
            )
            entry = aligned["start_s"]
            # Never hold longer than a bar: waiting is dead air in the plan and
            # the next line is at most one bar away by construction.
            if 0 < aligned["wait_s"] <= aligned["out_bar_s"] + 1e-6:
                time.sleep(aligned["wait_s"])

        free = 1 - self.active
        result = self.decks[free].play(
            incoming,
            start_s=entry,
            tempo_ratio=ratio,
            fade_in_s=fade,
        )
        if not result.get("ok"):
            return result
        self.active = free
        self.played.append(incoming)
        self._emit("TransitionStarted")
        self._emit("TrackPlaying")
        return {**result, "tempo_ratio": ratio, "fade_s": fade, "aligned": aligned}

    def skip(self) -> dict[str, Any]:
        """Cut to the next track now — no blend, because the DJ said now."""
        self.decks[self.active].stop()
        return self.start()

    def stop(self) -> None:
        for deck in self.decks:
            deck.stop()
        self._emit("SessionEnd")

    def due_for_blend(self) -> bool:
        """Is the outgoing track close enough to its end to start the next?"""
        live = self.decks[self.active].state()
        remaining = live.get("remaining_s")
        if remaining is None or not live["playing"]:
            return False
        if self.decks[1 - self.active].is_playing():
            return False          # already blending
        return remaining <= self.blend_s

    def tick(self) -> dict[str, Any]:
        """Advance the session. Safe to call every TUI redraw.

        The whole live behaviour lives here: when the current track nears its
        end, the NEXT choice is made — not before — so anything the DJ said in
        the meantime counts.
        """
        live = self.decks[self.active].state()
        if not live["playing"] and not self.decks[1 - self.active].is_playing():
            if self.played:
                return self.start()
        elif self.due_for_blend():
            return self.blend_into_next()
        return {"ok": True, "idle": True}

# Solo report T-0552

Files: plugins/sdlc-lite/scripts/fleet_doctor.py (new), plugins/sdlc-lite/skills/fleet-doctor/SKILL.md (new), .sdlc/0552-fleet-doctor-skill/live-probe.sh (new), handoff.md (## Acceptance criteria added).

- `python3 plugins/sdlc-lite/scripts/fleet_doctor.py selftest` exit 0
- `test "$(python3 plugins/sdlc-lite/scripts/fleet_doctor.py selftest | grep -c 'negative control: silent')" -eq 7` exit 0
- `bash .sdlc/0552-fleet-doctor-skill/live-probe.sh` exit 0
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0
- `python3 scripts/check-packaging.py` exit 0
- `python3 plugins/sdlc-lite/scripts/prompt_lint.py` exit 0
- `test -z "$(git diff --name-only HEAD -- . ':(exclude).sdlc')"` exit 0
- `python3 -c "import sys; sys.exit(any(chr(0x2014) in open(p).read() for p in sys.argv[1:]))" plugins/sdlc-lite/scripts/fleet_doctor.py plugins/sdlc-lite/skills/fleet-doctor/SKILL.md` exit 0
- `fleet_doctor.py selftest` exit 127 (Done-when shorthand, not a command from the repo root: the script is not on PATH; criterion 1 runs the same selftest as `python3 plugins/sdlc-lite/scripts/fleet_doctor.py selftest`, exit 0)

verify: needed (verifier L2: try 1 fail on boundary controls, fixed; try 2 pass, verifier-L2-2.md)

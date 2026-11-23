# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (text recon done; graphics static sweep partly reviewed). Last build: none yet (original ISO smoke-boots, 2026-11-23).
- **Done:** Step 0 (repo, rom.sha1, check + pre-commit hook rejecting failing tests, guard canary blocked, PPSSPP headless + windowed v1.20.4, boot route `tools/routes/boot.txt`, smoke passes on the original). Recon: CROW.PAK + .zdv formats (`docs/re/pak.md`, `tools/pak.py`, `tools/zdv.py`, `tools/unpack_all.py`), script/table/EBOOT text located and described (`docs/re/text.md`), decrypted EBOOT dumped to `work/exe/`. No prior fan patch exists.
- **Next:** finish phase 1 graphics survey: regenerate sheets (`docs/re/graphics.md` has the command per group), read every unreviewed group's sheets and fill the table's Japanese-cells column (title done). Then phase 2 (debug tool: warp to scenes; the .pwx block index / .ksf is the likely scene id - find the script loader in the EBOOT).
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) movie text: STORYTITLE01-10 chapter cards and the ending/credits movies are H.264 PMF with burned-in Japanese; re-encoding them is its own project. Default: plan to re-encode the chapter cards and credits (D5 says translate all graphics text) unless the owner says to leave movies Japanese.

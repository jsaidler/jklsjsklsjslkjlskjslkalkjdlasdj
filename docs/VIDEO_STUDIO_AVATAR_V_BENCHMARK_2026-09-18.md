# Local Video Studio — HeyGen Avatar V behavioral-identity benchmark

Date: **2026-09-18**  
Status: **NEXT PRODUCTION BENCHMARK / THREE SOURCES INVENTORIED / CONTACT-SHEET BUG FIXED / SOURCE ROLE REVIEW NEXT / NO AVATAR RESULT YET**

Canonical project state: `docs/PROJECT_STATE.md`.

## Purpose

This benchmark tests the requirement that previous static-image + audio renderers did not test:

> Can a generated video use completely new words while preserving João's recognizable expressions, gestures, head movement, posture and delivery rhythm from his real footage?

The benchmark is primarily a **behavioral-identity test**.

## Why Avatar V / Digital Twin

Current HeyGen documentation separates appearance, voice and motion. The Digital Twin is trained from real footage and Avatar V is specifically intended to reuse a person's own gestures, expressions and mannerisms rather than generalized presenter motion.

Official references:

- `https://help.heygen.com/en/articles/14602974-avatar-v-is-now-available-on-heygen`
- `https://help.heygen.com/en/articles/14602997-how-to-get-the-best-results-with-avatar-v-in-heygen`
- `https://help.heygen.com/en/articles/8389138-digital-twin-video-avatar-filming-tips`
- `https://help.heygen.com/en/articles/9964694-avatar-looks-explained`
- consent: `https://help.heygen.com/en/articles/12092609-recording-your-consent-video`

## Current product distinction — LOCKED

Do not collapse all HeyGen inputs into a single arbitrary 15-second clip.

Current HeyGen guidance exposes two related but distinct footage roles:

1. **Digital Twin / Video Look source footage** — current filming guidance recommends at least **2 minutes of uninterrupted speech** for a strong Digital Twin; adding a Video Look requires **2+ minutes** of footage with the person's face visible.
2. **Avatar V motion reference** — Avatar V guidance emphasizes about **15 seconds** of representative motion/reference footage as the critical motion-style input.

These are not interchangeable preparation steps. The project must first determine which of João's existing source videos are suitable for the base Digital Twin/Video Look role and which provide the best motion identity. Only then should any short motion segment be selected if the provider requires one.

## Existing source library — INVENTORIED 2026-09-18

Source folder:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

Technical inventory completed successfully for three originals:

| Source | Duration | Resolution | Digital Twin >=2 min | Avatar V >=15 s |
|---|---:|---:|---|---|
| `SIENA_BRUTO.mp4` | 113.3 s | 1080x1920 | NO | YES |
| `VID_20260819_124008056.mp4` | 282.6 s | 1920x1080 | YES | YES |
| `VID_20260911_140124885.mp4` | 300.4 s | 3840x2160 | YES | YES |

Interpretation:

- `VID_20260819_124008056.mp4` and `VID_20260911_140124885.mp4` both clear the current long-footage duration gate for the base Digital Twin/Video Look role.
- `VID_20260911_140124885.mp4` has the strongest technical resolution at 4K, but resolution alone does **not** make it the behavioral winner; framing, uninterrupted speech, natural mannerisms, visible gestures, gaze, lighting and cuts still need review.
- `SIENA_BRUTO.mp4` is below the current 2-minute base-source gate, but remains valid behavioral/motion-reference material because it is well over 15 seconds.
- Preserve all three originals exactly as supplied.

Inventory manifest:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\review\avatar_v_source_inventory.json`

Inventory report from this run:

`tools/video-studio/reports/avatar_v_source_inventory_20260918_170453.txt`

## Contact-sheet failure — DIAGNOSED / FIXED

The first inventory run successfully probed all three videos and wrote the manifest, but contact-sheet generation failed for each source with FFmpeg errors such as:

```text
Error opening input file -vf.
```

Cause: the PowerShell helper used a parameter named `$Input`, which conflicts with PowerShell's automatic `$input` variable (case-insensitive). The FFmpeg `-i` argument therefore received no file path and consumed `-vf` as the supposed input filename.

Patch applied to `tools/video-studio/inventory_avatar_v_sources.ps1`:

- renamed the helper parameters to `SourcePath` and `DestinationPath`;
- builds FFmpeg arguments as an explicit array;
- contact-sheet failure is now fatal instead of silently producing an empty manifest field;
- technical inventory logic is unchanged.

The original inventory values above remain valid. Rerun the patched inventory only to regenerate the three contact sheets and refresh the manifest with their paths.

## Source review policy — LOCKED

Source selection is based on representativeness, not maximum motion or maximum resolution.

The strongest base source should show as much as possible of:

- João speaking naturally and continuously;
- normal facial-expression range;
- characteristic head timing;
- typical hand/arm gestures;
- normal posture and idle behavior;
- direct enough gaze for reliable avatar training;
- stable lighting/focus;
- no disruptive cuts inside the useful section;
- clean enough speech audio for provider ingestion.

Do not choose a source merely because it is 4K, longer, more energetic or contains larger gestures. The target is **recognizable João behavior**.

## Creation strategy after visual review

After contact sheets are available and the actual videos are behaviorally reviewed:

1. assign the strongest qualifying long source to the **Digital Twin / Video Look** role;
2. retain the other long source as alternate behavioral/profile evidence rather than discarding it;
3. retain `SIENA_BRUTO.mp4` as valid motion-reference material even though it is below two minutes;
4. choose a representative Avatar V motion reference only when the current provider UI actually requires/accepts it;
5. complete the required live consent recording;
6. generate one short video with a **new Portuguese script not spoken in the reference material**;
7. use no custom motion prompt for the first gate;
8. judge visual identity and behavioral identity separately.

## First script policy

The test text must be ordinary and should not instruct the avatar to act, smile, be serious, gesture or perform an emotion. The behavior should come from the learned personal motion identity.

Suggested first benchmark text:

> Hoje eu estava pensando numa coisa simples: quando uma ferramenta começa a exigir mais atenção do que o próprio trabalho, talvez seja hora de rever o caminho e escolher outra solução.

If this text appears in any reference source, replace it before generation.

## Voice for first benchmark

The first benchmark may use HeyGen's standalone voice clone if convenient, but voice is scored separately. Do not delay the behavioral-identity gate solely to integrate CosyVoice.

## Pass criteria

The benchmark passes only if both are true:

1. **Visual identity:** the person remains convincingly João.
2. **Behavioral identity:** João recognizes his own mannerisms in the new performance rather than a generic avatar/presenter performance.

Behavioral checks include facial-expression range, eyebrow/eye behavior, head timing, hand/arm gesture language, posture, idle behavior, pauses/emphasis and absence of caricatured or repetitive presenter choreography.

## Failure interpretation

- **Looks right, moves wrong:** behavioral-identity fail; do not paper over with prompt tuning.
- **Moves right, looks wrong:** visual/look pipeline problem; the motion model may still be useful.
- **Both wrong:** reject this Avatar V/Digital Twin route.
- **Both right:** promote it to production-renderer integration and proceed to look/scene flexibility plus final voice-stage integration.

## Evidence to retain

Record provider/model, avatar/profile ID, original source filenames and SHA-256, assigned source roles, selected motion-reference source/time range or provider asset ID, selected look, test script, voice source, generation duration, credit/cost usage, final MP4 and João's separate visual/behavioral verdicts.

## Immediate action

1. Pull the contact-sheet fix.
2. Rerun `tools/video-studio/inventory_avatar_v_sources.ps1`; no source is modified.
3. Confirm that all three contact-sheet JPGs are generated under `review\contact_sheets`.
4. Review framing/coverage from the sheets and behavioral suitability from the original videos.
5. Assign the base Digital Twin source between the two >=2-minute candidates only after that review.
6. Do not trim, upload or return to Wan/H3/Hunyuan before source roles are settled.

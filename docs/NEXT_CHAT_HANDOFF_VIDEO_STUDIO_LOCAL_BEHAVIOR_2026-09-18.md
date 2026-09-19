# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **DWPose CPU SMOKE PASS / VISUAL POSE GATE NEXT**

## Continuation prompt

Continue o projeto **Local Video Studio** exatamente do estado canônico no GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`.

Antes de alterar qualquer estado, leia:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`
5. este arquivo;
6. `tools/video-studio/extract_dwpose_track.py`
7. `tools/video-studio/render_pose_overlay.py`
8. `tools/video-studio/run_behavior_pose_visual_gate.ps1`
9. `tools/video-studio/extract_behavior_profile.py`
10. `tools/video-studio/behavior_profile_schema_v1.json`

Não reconstruir decisões pela memória quando os documentos disserem algo diferente. Toda mudança de estado atualiza os documentos vivos.

## Restrições inegociáveis

- 100% local/self-hosted;
- zero custo de serviço;
- nenhum vídeo/voz/identidade do João enviado a terceiros;
- nada de SaaS/API paga/créditos/assinaturas;
- não baixar outro renderer grande;
- não retomar Wan S2V, H3 ou Hunyuan como próxima etapa;
- MuseTalk/LatentSync/TTS final continuam deferidos;
- não instalar outro Python, outro DWPose ou dependências CUDA antes de evidência de necessidade.

## Objetivo

Novo texto/áudio deve gerar performance nova que:

1. pareça João;
2. soe como João;
3. principalmente, mova-se e reaja como João.

Movimento genérico não basta.

## Arquitetura

```text
vídeos reais do João
    -> pose + prosódia local
    -> motion units persistentes

novo áudio
    -> janelas prosódicas
    -> seleção/ordenação por compatibilidade
    -> continuidade de pose + diversidade
    -> nova performance composta do vocabulário real de João

novo driving video
    -> Wan-Animate-2 já instalado
    -> lip-sync local posteriormente se necessário
```

## Fonte primária

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4`

300.352 s / 3840x2160 HEVC + áudio.

## Estado validado em 2026-09-19

### DWPose local

Reuse confirmado:

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

Não baixar outro pose stack.

### Runtime probe

Inferência real de um frame passou e produziu `coco_wholebody_133` sem detector fallback.

ONNX Runtime anunciou CUDA/TensorRT/CPU, mas a tentativa CUDA emitiu erro por dependência ausente `cublasLt64_13.dll`. Portanto:

- DWPose funcional: **PASS**;
- CUDA ORT efetivo: **FAIL / não validado**;
- não instalar CUDA agora; CPU continua suficiente para o gate.

### Smoke CPU

Trecho 30–35 s, 6 fps, 960x540, CPU:

```text
frames: 30
detector_fallback_frames: 0
detector_fallback_ratio: 0.0
mean_keypoint_score: 0.13263878929229625
elapsed_s: 26.750566244125366
frames_per_second_wall: 1.1214715877869776
```

Track existente:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_smoke_5s.jsonl`

O score médio isolado não é critério suficiente para aprovar qualidade anatômica.

## Visual gate — PRÓXIMA AÇÃO EXATA

Foi versionado:

- `tools/video-studio/render_pose_overlay.py`;
- `tools/video-studio/run_behavior_pose_visual_gate.ps1`.

Eles não rodam DWPose novamente. Apenas desenham o track já extraído sobre os frames correspondentes e geram:

`Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_smoke_5s_overlay.mp4`

Rodar:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_pose_visual_gate.ps1'
```

Depois abrir o MP4 e verificar:

- torso/braços sobre a anatomia correta;
- mãos ligadas aos pulsos corretos;
- landmarks de dedos plausíveis;
- face acompanhando o rosto;
- ausência de saltos, swaps esquerda/direita e tracking do fundo.

**Não executar o full 300 s antes desse gate visual passar.**

## Depois do visual PASS

1. gerar full pose track da fonte primária a 6 fps;
2. gerar behavior profile com `status=complete`;
3. inspecionar `manifest.json` + `motion_units.csv`;
4. compor novo driving video de 4–5 s usando várias motion units;
5. só então executar Wan-Animate-2.

## Qualidade final

> “isso não apenas parece João; isso se move e reage como João.”

Nenhuma métrica automática substitui esse julgamento.

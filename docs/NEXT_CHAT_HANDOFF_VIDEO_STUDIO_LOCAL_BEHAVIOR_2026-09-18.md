# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **DWPose CPU SMOKE PASS / FIRST SAMPLE REJECTED BY OCCLUSION / C3 CLEAN VISUAL GATE SELECTED**

## Continuation prompt

Continue o projeto **Local Video Studio** exatamente do estado canônico no GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`.

Antes de alterar estado, leia:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`
5. este arquivo;
6. `tools/video-studio/extract_dwpose_track.py`
7. `tools/video-studio/render_pose_overlay.py`
8. `tools/video-studio/run_behavior_pose_selected_gate.ps1`
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

## Estado validado em 2026-09-19

### Local DWPose

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

ONNX Runtime anunciou CUDA/TensorRT/CPU, mas CUDA emitiu erro por `cublasLt64_13.dll` ausente. Portanto:

- DWPose funcional: **PASS**;
- CUDA ORT efetivo: **FAIL / não validado**;
- CPU é o caminho atual do gate.

### Smoke CPU

Trecho 30–35 s, 6 fps, 960x540:

```text
frames: 30
detector_fallback_frames: 0
detector_fallback_ratio: 0.0
mean_keypoint_score: 0.13263878929229625
elapsed_s: 26.750566244125366
frames_per_second_wall: 1.1214715877869776
```

Resultado técnico: PASS.

### Primeiro visual gate

30–35 s foi rejeitado como amostra porque João estava segurando um objeto grande, ocultando mãos e cruzando o torso. Isso não foi classificado como falha do DWPose.

### Candidate sampler

O contact sheet com oito janelas foi gerado e inspecionado. A janela escolhida é:

**C3 = 88.7 s → 93.7 s.**

Motivos:

- duas mãos livres e visíveis;
- gesticulação real ao longo dos 5 s;
- torso, braços e pulsos desobstruídos;
- nenhuma peça segurada cruzando a anatomia;
- desafio melhor que candidatos mais estáticos.

C2 seria utilizável, mas C3 é o gate canônico.

## Próxima ação exata

Runner versionado:

`tools/video-studio/run_behavior_pose_selected_gate.ps1`

Ele executa apenas:

1. DWPose CPU no trecho 88.7–93.7 s, 6 fps;
2. overlay visual desse mesmo track.

Rodar:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_pose_selected_gate.ps1'
```

Saídas:

```text
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\selected_gate\pose_gate_c3_88p7_93p7_coco133.jsonl
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\selected_gate\pose_gate_c3_88p7_93p7_coco133.jsonl.summary.json
Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\selected_gate\pose_gate_c3_88p7_93p7_overlay.mp4
```

Uploadar o overlay MP4. Validar:

- torso/braços sobre a anatomia correta;
- pulsos e mãos ligados corretamente;
- dedos plausíveis;
- face estável;
- ausência de swaps esquerda/direita e saltos temporais.

**Não executar full 300 s antes do visual PASS.**

Depois do PASS:

1. gerar full pose track a 6 fps;
2. gerar behavior profile `status=complete`;
3. inspecionar `manifest.json` + `motion_units.csv`;
4. compor novo driving video de 4–5 s com várias motion units;
5. só então executar Wan-Animate-2.

## Qualidade final

> “isso não apenas parece João; isso se move e reage como João.”

Nenhuma métrica automática substitui esse julgamento.

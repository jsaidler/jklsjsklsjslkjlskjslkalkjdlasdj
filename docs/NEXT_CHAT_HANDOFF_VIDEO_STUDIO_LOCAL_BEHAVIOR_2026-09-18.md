# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **DWPose runtime PASS / C3 VISUAL GATE FAILED FROM ORIENTATION BUG / ORIENTATION FIX IMPLEMENTED / C3 RERUN NEXT**

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

## Estado validado

### DWPose local

Reuse confirmado:

```text
Z:\AI\WanGP\env_uv\Scripts\python.exe          Python 3.11.14
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx
```

DWPose funcional: PASS. CUDA ORT efetivo continua não validado por ausência de `cublasLt64_13.dll`; CPU é o caminho atual.

### Clean gate interval

C3 = **88.7 s → 93.7 s**.

Foi escolhido por ter duas mãos livres, gesticulação real e torso/pulsos desobstruídos.

### C3 overlay recebido — FAIL

O overlay enviado mostrou:

- esqueleto corporal atravessando rosto/torso;
- face geometricamente instável;
- algumas mãos localmente plausíveis, mas geometria corporal global inutilizável.

Não classificar isso ainda como falha do modelo DWPose.

## Root cause identificado

A fonte primária tem dimensões codificadas 3840x2160, mas é exibida em portrait através de metadata de rotação.

O extrator anterior:

1. calculava tamanho de análise a partir das dimensões codificadas;
2. escolhia 960x540;
3. FFmpeg autorotacionava o frame para portrait;
4. o pipeline então forçava esse portrait já rotacionado para 960x540;
5. DWPose recebia a pessoa severamente achatada.

Isso explica a geometria ruim observada no overlay.

## Fix implementado

`tools/video-studio/extract_dwpose_track.py` agora:

- lê `rotation` de stream side-data ou tag `rotate` via ffprobe;
- mantém dimensões codificadas separadas das dimensões de display;
- troca width/height para rotações 90°/270°;
- calcula a resolução de análise a partir da orientação de display usada pelo autorotate do FFmpeg;
- grava no summary:
  - `coded_width` / `coded_height`;
  - `display_width` / `display_height`;
  - `rotation_degrees`;
  - `analysis_width` / `analysis_height`.

Para a fonte primária, a reexecução correta deve resultar em análise portrait, aproximadamente **540x960**, e não 960x540.

## Próxima ação exata

Rerodar o mesmo gate C3; o runner sobrescreve o track e overlay antigos:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\run_behavior_pose_selected_gate.ps1'
```

Depois:

1. conferir no summary se `analysis_width`/`analysis_height` estão em portrait (~540x960);
2. uploadar o novo `pose_gate_c3_88p7_93p7_overlay.mp4`;
3. validar torso/braços, pulsos/mãos/dedos, face, swaps e saltos temporais;
4. somente após visual PASS gerar full pose track a 6 fps;
5. gerar behavior profile `status=complete`;
6. inspecionar `manifest.json` + `motion_units.csv`;
7. compor novo driving video de 4–5 s com várias motion units;
8. só então executar Wan-Animate-2.

## Qualidade final

> “isso não apenas parece João; isso se move e reage como João.”

Nenhuma métrica automática substitui esse julgamento.

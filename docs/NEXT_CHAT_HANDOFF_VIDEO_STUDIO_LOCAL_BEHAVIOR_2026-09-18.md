# Next chat handoff — Video Studio local behavioral route

Updated: **2026-09-19**  
Status: **LOCAL DWPOSE FOUND / WANGP RUNTIME PROBE NEXT**

## Continuation prompt

Continue o projeto **Local Video Studio** exatamente do estado canônico no GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`.

Antes de alterar qualquer estado, leia:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`
5. este arquivo;
6. `tools/video-studio/probe_wangp_dwpose_runtime.ps1`
7. `tools/video-studio/extract_dwpose_track.py`
8. `tools/video-studio/run_behavior_pose_smoke.ps1`
9. `tools/video-studio/extract_behavior_profile.py`
10. `tools/video-studio/behavior_profile_schema_v1.json`

Não reconstruir decisões pela memória quando os documentos disserem algo diferente. Toda mudança de estado atualiza os documentos vivos.

## Restrições inegociáveis

- 100% local/self-hosted;
- zero custo de serviço;
- nenhum vídeo/voz/identidade do João enviado a terceiros;
- nada de HeyGen/Kling/SaaS/API paga/créditos/assinaturas;
- não baixar outro renderer grande;
- não retomar Wan S2V, H3 ou Hunyuan como próxima etapa;
- MuseTalk/LatentSync e final TTS continuam deferidos;
- não instalar outro Python nem outro DWPose enquanto a reutilização local ainda está sendo validada.

## Objetivo

Novo texto/áudio deve gerar performance nova que:

1. pareça João;
2. soe como João;
3. principalmente, mova-se e reaja como João.

Movimento genérico/natural não basta.

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

## Fonte primária atual

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4`

300.4 s / 3840x2160 HEVC + áudio.

## Estado resolvido em 2026-09-19

### Windows launcher

```text
py -3.11: NOT RESOLVED
```

O launcher do Windows não possui Python 3.11 registrado. Isso **não** implica instalar Python.

Já existe histórico de runtime WanGP isolado validado em:

`Z:\AI\WanGP\env_uv\Scripts\python.exe`

O projeto já o usou como Python 3.11.14 / Torch 2.10.0+cu130 / CUDA 13.0.

### DWPose local — encontrado

```text
Z:\AI\WanGP\preprocessing\dwpose
Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx   ~128.2 MB
Z:\AI\WanGP\ckpts\pose\yolox_l.onnx           ~206.7 MB
```

Portanto:

**NÃO BAIXAR DWPose-L, ControlNet Aux ou outro pose stack.**

## Tooling novo já versionado

### `probe_wangp_dwpose_runtime.ps1`

Valida o `env_uv`, imports, providers ONNX e uma inferência real detector + 133 keypoints em um frame da fonte primária. Sem download/instalação/model mutation.

### `extract_dwpose_track.py`

Extrai track normalizado `coco_wholebody_133` em JSONL usando o WanGP existente. Full pass eventual: 6 fps, análise 960 px no lado maior, provider auto CUDA->CPU.

### `run_behavior_pose_smoke.ps1`

Smoke de ~5 s / 4 fps, pose somente. Produz track + summary com provider, fallback ratio, confiança e throughput.

### `extract_behavior_profile.py`

Combina pose real + motion/prosody local e produz `manifest.json` + `motion_units.csv`. Só `status=complete` passa o gate. `incomplete_pose` é diagnóstico apenas.

## Próxima ação exata

Rodar somente o runtime probe:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\probe_wangp_dwpose_runtime.ps1'
```

Não rodar o smoke automaticamente se o probe falhar. Corrigir o runtime existente primeiro.

Se o probe passar:

1. executar `run_behavior_pose_smoke.ps1`;
2. verificar 133 keypoints, provider, fallback ratio, confiança e throughput;
3. gerar full pose track a 6 fps;
4. gerar behavior profile `status=complete`;
5. inspecionar inventário;
6. montar novo driving video de 4–5 s com várias motion units;
7. só então executar Wan-Animate-2.

## Qualidade

Gate humano:

> “isso não apenas parece João; isso se move e reage como João.”

Nenhuma métrica automática substitui esse julgamento.

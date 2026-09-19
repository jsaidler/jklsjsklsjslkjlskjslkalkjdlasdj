# Next chat handoff — Video Studio local behavioral route

Date: **2026-09-18**  
Status: **BEHAVIOR PROFILE IMPLEMENTATION STARTED / LOCAL PYTHON+POSE INSPECTION NEXT**

Paste the prompt below into the next chat.

---

## Continuation prompt

Continue o projeto **Local Video Studio** exatamente do estado canônico no GitHub `jsaidler/jklsjsklsjslkjlskjslkalkjdlasdj`, branch `main`.

Antes de responder ou propor qualquer alteração, leia integralmente, nesta ordem:

1. `docs/PROJECT_STATE.md`
2. `docs/VIDEO_STUDIO_LOCAL_ZERO_COST_POLICY_2026-09-18.md`
3. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_ROUTE_2026-09-18.md`
4. `docs/VIDEO_STUDIO_LOCAL_BEHAVIOR_PREFLIGHT_2026-09-18.md`
5. `docs/NEXT_CHAT_HANDOFF_VIDEO_STUDIO_LOCAL_BEHAVIOR_2026-09-18.md`
6. `docs/VIDEO_STUDIO_DIRECTION_RESET_2026-09-15.md`
7. `docs/VIDEO_STUDIO.md`
8. `docs/VIDEO_STUDIO_QUALITY_GATE_2026-09-15.md`
9. `tools/video-studio/preflight_local_behavior_route.ps1`
10. `tools/video-studio/inspect_local_behavior_tooling.ps1`
11. `tools/video-studio/behavior_profile_schema_v1.json`
12. `tools/video-studio/extract_behavior_profile.py`

Não reconstrua decisões por memória se os documentos disserem algo diferente. Atualize os documentos vivos sempre que o estado mudar.

### Restrições inegociáveis

O projeto é **100% local/self-hosted e sem custos de serviço**. Não usar HeyGen, Kling, APIs pagas, créditos, assinaturas, SaaS/cloud inference ou qualquer plataforma externa de geração/treino/avatar. Não enviar vídeos, voz ou identidade do João para terceiros. Internet pode ser usada apenas para pesquisa/documentação e download de componentes gratuitos que rodem localmente. Não escolher software/modelo/licença paga sem autorização explícita prévia.

Não baixar outro renderer grande. Wan S2V, H3, Hunyuan e HeyGen não são a próxima etapa. MuseTalk/LatentSync e CosyVoice continuam deferidos até o gate comportamental.

### Objetivo real

Gerar vídeos novos a partir de novo texto/áudio em que o resultado:

- pareça visualmente com João;
- soe como João;
- **mova-se e expresse-se como João**, preservando sua identidade comportamental real.

Movimento apenas plausível ou “natural” não basta.

### Arquitetura escolhida

```text
vídeos reais do João
    -> pose + prosódia
    -> biblioteca persistente de motion units do próprio João

novo áudio local
    -> janelas prosódicas
    -> busca/ordenação de motion units compatíveis
    -> continuidade de pose + diversidade
    -> novo driving video composto da linguagem corporal real do João

novo driving video
    -> Wan-Animate-2 já instalado
    -> lip-sync local depois, se necessário
```

Não usar um único driving clip fixo.

### Fontes comportamentais canônicas

Pasta:

`Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\`

- `VID_20260911_140124885.mp4` — 300.4 s, 3840x2160 HEVC + áudio — **primeiro alvo e fonte principal de tronco/mãos/postura/gestos**;
- `VID_20260819_124008056.mp4` — 282.6 s, 1920x1080 H.264 + áudio — facial/microexpressões;
- `SIENA_BRUTO.mp4` — 113.3 s, 1080x1920 H.264 + áudio — gestos/visual alternativo, excluindo spans problemáticos quando necessário.

### Preflight já concluído

```text
BEHAVIOR SOURCES: PASS
WAN-ANIMATE-2 PAYLOAD: PASS
WAN-ANIMATE-2 NATIVE CODE: PASS
POSE TOOLING: NOT FOUND UNDER WAN ROOT
NEXT ROUTE GATE: BUILD BEHAVIOR PROFILE WITHOUT NEW LARGE RENDERER DOWNLOAD
```

Wan-Animate-2 reutilizável:

- `Z:\AI\WanAnimate2\models\diffusion_models\wan_animate_2_bf16.safetensors` — 30.538 GiB;
- `Z:\AI\WanAnimate2\models\text_encoders\umt5_xxl_fp16.safetensors` — 10.586 GiB;
- `Z:\AI\WanAnimate2\models\vae\Wan2_1_VAE_bf16.safetensors` — 0.236 GiB;
- `Z:\AI\WanAnimate2\comfy\ldm\wan\model_animate2.py` — presente.

### Implementação já versionada

`tools/video-studio/inspect_local_behavior_tooling.ps1`

- somente leitura;
- resolve o executável real de `py -3.11` e valida `sys.version_info`;
- procura candidatos Python existentes nos runtimes locais;
- procura DWPose/whole-body/hand pose de forma direcionada e limitada nos roots prováveis;
- não instala, não baixa, não apaga e não varre cegamente todo `Z:`;
- produz TXT/JSON local em `tools/video-studio/reports/`.

`tools/video-studio/behavior_profile_schema_v1.json`

- schema persistente `behavior-profile/v1`;
- motion unit guarda source/timestamps/RGB span, pose inicial/final, head/hand/body activity, motion energy, speech/pause, prosódia disponível e descritores de transição.

`tools/video-studio/extract_behavior_profile.py`

- primeiro alvo: `VID_20260911_140124885.mp4`;
- base renderer-independent e sem dependência nova: FFmpeg/ffprobe + stdlib Python;
- energia visual por diferenças de frames grayscale de baixa resolução;
- prosódia v1 por RMS/dBFS, energia normalizada e fala/pausa;
- cortes priorizam pausa + baixa energia;
- aceita pose normalizada por JSONL para não acoplar o schema ao backend;
- gera `manifest.json` + `motion_units.csv` inspecionáveis;
- sem pose só roda mediante `--allow-missing-pose` e produz `status=incomplete_pose`;
- **`incomplete_pose` nunca passa o gate comportamental**.

### Python continua não resolvido até o probe local

O preflight antigo imprimiu:

`Python 3.11: PASS / C:\Python314\python.exe / 3.14.3`

Isso não valida Python 3.11. O novo inspector existe justamente para resolver a discrepância pela versão reportada pelo próprio executável.

Não reinstalar Python cegamente.

### Pose tooling continua não resolvido até o probe local

A ausência anterior era somente sob `Z:\AI\WanAnimate2`. Primeiro executar o novo inspector. Reutilizar o que existir.

Se nada compatível existir, só então pesquisar a menor dependência necessária e informar **arquivo exato, fonte oficial, licença, tamanho, destino, espaço final e motivo** antes de qualquer download.

### Disco

No último preflight Z: tinha ~22.32 GB livres. O payload aposentado abaixo continua apenas como candidato de limpeza se surgir necessidade real:

`Z:\AI\WanGP\ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors` — 12.486 GiB.

Não apagar por reflexo.

### O que fazer agora

A próxima ação é rodar **somente** o inspector versionado na máquina local, após atualizar o repositório:

```powershell
cd 'D:\GOOGLE DRIVE\DEV\Roguelite'

git pull --ff-only origin main

powershell -ExecutionPolicy Bypass -File '.\tools\video-studio\inspect_local_behavior_tooling.ps1'
```

Depois, usar o relatório para:

1. escolher explicitamente o interpreter correto;
2. reutilizar pose tooling local, se houver;
3. ou, se realmente ausente, especificar a menor dependência antes do download;
4. implementar o adapter de pose para o JSONL normalizado;
5. gerar o primeiro profile `status=complete` para `VID_20260911_140124885.mp4`;
6. revisar `manifest.json` e `motion_units.csv`;
7. só então montar uma nova performance de ~4–5 s com várias motion units;
8. só depois executar Wan-Animate-2.

Não rodar Wan-Animate-2 antes do perfil completo.

### Regra de qualidade

O gate humano continua:

> “isso não apenas parece João; isso se move e reage como João.”

### Forma de trabalho

- usar GitHub e documentos vivos;
- não criar decisões paralelas apenas no chat;
- preferir scripts `.ps1`/`.py` versionados;
- corrigir scripts no repositório em vez de pedir grandes blocos de depuração manual;
- todo comando local após mudança remota começa por `cd ...` + `git pull --ff-only origin main`;
- não baixar/instalar nada sem especificação prévia;
- não apagar fontes comportamentais originais.

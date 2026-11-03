# mpvpn-lists

Central Split DNS templates for [MPVPN](https://github.com/KevinGandalf/mpvpn-full).

MPVPN loads these files at runtime (default: once a day, plus the
**Vorlagen aktualisieren** / *Update templates* button on the Split DNS page). A
change merged here reaches every MPVPN install on its next refresh – no new
release needed.

```
index.yaml              version + the template files that are used
templates/<id>.yaml     one template (streaming, banking, …) with its services
tools/validate.py       the same checks MPVPN runs before installing a version
```

## How MPVPN uses them

- A Split DNS list refers to a **template** (`template: streaming`) and/or to
  single **services** by key (`services: [banking/paypal]`). It does not copy
  the domains: when a service here gets a new domain, every list that contains
  the service uses it after the next refresh.
- Overrides send one service through another uplink
  (`overrides: {streaming/netflix: wg-de}`).
- The repository is read from
  `https://raw.githubusercontent.com/KevinGandalf/mpvpn-lists/main/`
  (configurable: `templates.url` in `config.yaml`, or `templates.disabled: true`
  for the built-in copy only).
- A version is installed only if **all** files are valid. A broken commit never
  removes templates that are in use – MPVPN keeps the last good version (cached
  on disk, so this also survives a reboot without internet). Each MPVPN binary
  also has a built-in copy for first boot and offline use.

**Keep IDs stable.** Template IDs (file names) and service IDs are what lists
store. Change names and domains freely. When a template or service has to be
renamed, moved or split, add an **alias** in `index.yaml` so lists that use the
old ID keep working:

```yaml
aliases:
  streaming: [streaming-de, streaming-us, streaming-uk, streaming-other]   # template
  streaming/netflix: [streaming-us/netflix]                                # service
  streaming/ard-zdf-arte: [streaming-de/ard, streaming-de/zdf, streaming-de/arte]
```

An alias must not have the name of an existing template or service, and every
target must exist. Never remove an alias – old lists may still use it.

## Templates

| ID | Content |
| --- | --- |
| `banking` | German banks, online banks, neobanks, brokers, payment services |
| `banking-international` | Banks in AT, CH, UK, US and Europe |
| `crypto` | Crypto exchanges |
| `streaming-de` | ARD, ZDF, arte, RTL+, Joyn, WOW/Sky, MagentaTV, waipu.tv, Zattoo, DAZN, … |
| `streaming-us` | Netflix, Disney+, Prime Video, Max, Hulu, Peacock, Paramount+, Apple TV+, … |
| `streaming-uk` | BBC iPlayer, ITVX, Channel 4, My5, NOW, Sky UK, BritBox, … |
| `streaming-other` | YouTube, Twitch, Crunchyroll, video platforms, broadcasters of other countries |
| `music` | Spotify, Apple Music, Deezer, Tidal, SoundCloud, Amazon Music |
| `gaming` | Stores, consoles, launchers, cloud gaming (GeForce NOW, Luna, Boosteroid) |
| `social` | Social networks and messengers |
| `video-calls` | Zoom, Teams, Webex, Meet, Jitsi |
| `mail-cloud` | Mail providers and cloud storage |
| `news` | National press DE/AT/CH and tech media |
| `news-international` | International press and agencies |
| `news-alternative` | Independent / non-mainstream media from across the political spectrum (a plain domain list, no endorsement) |
| `shopping` | Marketplaces, fashion, electronics, drugstores, DIY, groceries, travel, delivery |
| `ai` | ChatGPT, Claude, Gemini, Copilot, Perplexity, Mistral, DeepL |

The same domain may appear in two templates (e.g. `t-online.de` in mail and
news); in MPVPN the list with the lower priority value is checked first.

## File format

```yaml
id: streaming                 # = file name, a-z 0-9 -
name:
  de: Video-Streaming
  en: Video streaming
description:
  de: Netflix, Disney+, …
  en: Netflix, Disney+, …
priority: 0                   # -100..100, lower is checked first (banking: -10)
services:
  - id: netflix               # stable, a-z 0-9 -, unique in this template
    name: Netflix
    domains:
      - '**.netflix.com'
      - '**.nflxvideo.net'
```

New template: add `templates/<id>.yaml` **and** list it in `index.yaml`.
Bump `version` in `index.yaml` with every change (date, e.g. `2026.11.03`, add
`.1`, `.2` for several on one day) – it is shown in the admin UI.

## Domain patterns

| Pattern | Matches |
| --- | --- |
| `example.com` | exactly `example.com` |
| `*.example.com` | `example.com` and one level below (`www.example.com`) |
| `**.example.com` | `example.com` and every level below (`a.b.example.com`) |
| `sparkasse-*.de` | `*` inside one label: `sparkasse-koelnbonn.de` |
| `**.sparkasse-*.de` | the same with all subdomains |

Not allowed: URLs, ports or paths (`https://…`, `:443`, `/login`), a wildcard
in the top-level domain (`example.*`) and `*.de`-style patterns that would
match a whole TLD.

Prefer `**.service.com` for a service's own domains. Add CDN domains only if
they belong to that service alone (`**.nflxvideo.net` yes, a shared CDN such as
`**.akamaized.net` no – it would move unrelated sites too).

## Contributing

1. Edit or add a template.
2. `pip install pyyaml && python3 tools/validate.py`
3. Open a pull request – the `validate` workflow runs the same check.

Limits: 100 templates, 2000 services, 20000 patterns, 512 KiB per file.

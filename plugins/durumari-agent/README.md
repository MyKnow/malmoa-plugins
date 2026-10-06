# Durumari native Agent plugin

Codex와 Claude Code의 네이티브 플러그인 패키지입니다.

| 명령 | 역할 |
| --- | --- |
| `context` | 현재 프로젝트의 서버 Context 읽기·갱신 |
| `connect` | 기기별 로그인·프로젝트 연결 |
| `status` | 연결·현재 읽기 권한·대기 수집 진단 |
| `migrate` | 기존 문서와 첨부 검토·이전 |
| `update` | 최신 패키지 확인·업데이트 |

Claude Code에서는 `/durumari:context`, `/durumari:connect`, `/durumari:status`, `/durumari:migrate`로 실행합니다. Codex에서는 설치된 Durumari 스킬을 선택하거나 해당 작업을 요청합니다.

## 로컬 패키지 빌드·등록

저장소 루트에서 Python 3.12+와 uv를 사용합니다.

```sh
python3 plugins/durumari-agent/scripts/build_bundle.py --service-origin http://127.0.0.1:8000
codex plugin marketplace add .
codex plugin add durumari@durumari-local
claude plugin marketplace add .
claude plugin install durumari@durumari-local --scope local
```

Claude의 `local` 설치 범위는 명령을 실행한 작업 프로젝트입니다. 다른 프로젝트에도 사용하려면 그 프로젝트에서 설치하거나 명시적으로 user 범위를 선택합니다. Codex의 활성화 범위는 호스트 설정에 따릅니다. 새 세션에서 적용을 확인합니다. 위 명령은 개발용 로컬 카탈로그에 등록합니다. 공개 Directory 게시에는 별도 제출·심사가 필요합니다.

`runtime/`은 빌드 시 생성되는 wheel, 잠근 의존성, SHA-256 목록과 비밀값 없는 기본 서비스 주소입니다. 패키지 배포 시 반드시 포함합니다. 공개 배포 빌드에는 실제 HTTPS API 주소를 `--service-origin`으로 지정합니다. 위 loopback 주소는 이 Mac의 로컬 시험용입니다. 서비스 도메인 변경은 이 배포 설정에서 처리하며, 기존 프로젝트 manifest의 서버와 자격증명은 자동으로 옮기지 않습니다. 런타임 설치는 network를 통해 잠근 의존성을 내려받을 수 있습니다. 원본 코드의 바이너리 중복을 피하기 위해 이 폴더는 Git에서 제외합니다. 소스 코드만 설치했으면 먼저 빌드합니다.

## 연결 경계

플러그인에는 계정 자격증명이나 특정 프로젝트 ID·기기 경로가 없습니다. Agent가 기본 서비스 주소로 연결을 시작하고, 사용자는 브라우저에서 로그인·프로젝트 선택·공유 범위를 승인합니다. 프로젝트 자격증명은 OS 보호 저장소에 저장합니다. 기존 연결은 status로 그대로 확인합니다.

MCP와 자동 수집 hooks는 `connect`가 프로젝트에 설치합니다. 공용 플러그인 프로세스가 잘못된 프로젝트를 읽지 않도록 `durumari.yaml`과 해당 workspace에 명시적으로 연결합니다. 호스트의 정상 신뢰 승인이 필요합니다. 설정 파일 존재, 플러그인 목록, doctor 성공과 실제 모델 실행·수집 증거는 각각 구분합니다.

Durumari 서버가 Context 정본입니다. 기존 `/docs`는 이전 후 보존본이며 자동 양방향 동기화 대상이 아닙니다. 실제 접근은 서버 주소의 연결 범위에 따릅니다. localhost 서버는 다른 기기에서 접근 가능한 Cloud 배포가 아닙니다.

## Browser account connection

The agent runs connect without asking for a server address or IDs. The workspace manifest takes precedence over the installed package's service address. The browser handles signup/login, code comparison, project selection and collection consent. The process waits for human approval without terminal input. First accounts may explicitly create a personal space and a new restricted direct source. Existing source policies and pending queues are preserved. Local documents lead into a reviewed migration preview; uploads follow the user's authorized scope. Noninteractive connection refuses legacy terminal choices. `--password-login` remains an explicit human-terminal compatibility option.

Display name: 두루마리 / Durumari. Plugin/package/tool/store identifiers retain their original names for upgrade compatibility; `durumari-mcp` is the preferred executable alias. Installing this local skill package does not itself register a remote OAuth app or trigger the host’s install-time authorization screen.

## 이전 호스트 플러그인에서 전환

공개 설치기는 모든 대상 도구에서 새 버전을 확인한 뒤 정확히 일치하는 이전 사용자 플러그인만 호스트의 제거 명령으로 정리합니다. Claude의 플러그인 데이터는 보존하고 프로젝트 연결 파일·OS 자격 증명·대기 기록은 삭제하지 않습니다. 정리에 실패하면 새 설치를 되돌리지 않고 `legacy_cleanup_required`와 대상 도구를 반환합니다. 설치를 다시 실행하거나 해당 도구의 플러그인 관리에서 이전 플러그인을 해제한 뒤 새 세션을 시작하세요. 다른 카탈로그나 프로젝트 범위의 플러그인은 자동으로 제거하지 않습니다.

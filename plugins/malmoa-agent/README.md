# MALMOA native Agent plugin

Codex와 Claude Code의 네이티브 플러그인 패키지입니다.

| 명령 | 역할 |
| --- | --- |
| `context` | 현재 프로젝트의 서버 Context 읽기·갱신 |
| `connect` | 기기별 로그인·프로젝트 연결 |
| `status` | 연결·현재 읽기 권한·대기 수집 진단 |
| `migrate` | 기존 문서와 첨부 검토·이전 |
| `update` | 최신 패키지 확인·업데이트 |

Claude Code에서는 `/malmoa:context`, `/malmoa:connect`, `/malmoa:status`, `/malmoa:migrate`로 실행합니다. Codex에서는 설치된 MALMOA 스킬을 선택하거나 해당 작업을 요청합니다.

## 로컬 패키지 빌드·등록

저장소 루트에서 Python 3.12+와 uv를 사용합니다.

```sh
python3 plugins/malmoa-agent/scripts/build_bundle.py
codex plugin marketplace add .
codex plugin add malmoa@malmoa-local
claude plugin marketplace add .
claude plugin install malmoa@malmoa-local --scope local
```

Claude의 `local` 설치 범위는 명령을 실행한 작업 프로젝트입니다. 다른 프로젝트에도 사용하려면 그 프로젝트에서 설치하거나 명시적으로 user 범위를 선택합니다. Codex의 활성화 범위는 호스트 설정에 따릅니다. 새 세션에서 적용을 확인합니다. 위 명령은 개발용 로컬 카탈로그에 등록합니다. 공개 Directory 게시에는 별도 제출·심사가 필요합니다.

`runtime/`은 빌드 시 생성되는 wheel, 잠근 의존성, SHA-256 목록입니다. 패키지 배포 시 반드시 포함합니다. 런타임 설치는 network를 통해 잠근 의존성을 내려받을 수 있습니다. 원본 코드의 바이너리 중복을 피하기 위해 이 폴더는 Git에서 제외합니다. 소스 코드만 설치했으면 먼저 빌드합니다.

## 연결 경계

플러그인에는 계정 자격증명이나 특정 프로젝트 ID·기기 경로가 없습니다. 로그인은 사용자의 터미널에서 진행하며 OS 보호 저장소에 저장합니다. 기존 연결은 status로 그대로 확인합니다.

MCP와 자동 수집 hooks는 `connect`가 프로젝트에 설치합니다. 공용 플러그인 프로세스가 잘못된 프로젝트를 읽지 않도록 `malmoa.yaml`과 해당 workspace에 명시적으로 연결합니다. 호스트의 정상 신뢰 승인이 필요합니다. 설정 파일 존재, 플러그인 목록, doctor 성공과 실제 모델 실행·수집 증거는 각각 구분합니다.

MALMOA 서버가 Context 정본입니다. 기존 `/docs`는 이전 후 보존본이며 자동 양방향 동기화 대상이 아닙니다. 실제 접근은 서버 주소의 연결 범위에 따릅니다. localhost 서버는 다른 기기에서 접근 가능한 Cloud 배포가 아닙니다.

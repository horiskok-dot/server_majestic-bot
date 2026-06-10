# TECHNICAL_FILES_REPORT.md

Сгенерировано: `2026-04-26 22:11:34`
Проект: `/home/pc/PCControlPersonal_Project`

Секреты, пароли, токены Telegram, `SERVER_ACCESS_KEY`, `ADMIN_TOKEN`, JWT и похожие значения в этом отчёте не выводятся. Если такие значения встречались, они маскируются как `[HIDDEN]`.

## 1. Краткое состояние проекта

- Всего файлов проанализировано: `712`.
- Важных файлов подробно разобрано: `340`.
- Git status: Git-репозиторий не обнаружен.
- Основная цель проекта: личный сервер PC Control Personal для управления собственными агентами через FastAPI, Telegram-бота, веб-панель и Android-приложение.

## 2. Дерево проекта без мусора

```text
PCControlPersonal_Project/
├── .env.example
├── android-app/
│   ├── .codex-tools/
│   │   ├── gradle-7.6/
│   │   │   ├── bin/
│   │   │   │   ├── gradle
│   │   │   │   └── gradle.bat
│   │   │   ├── init.d/
│   │   │   │   └── readme.txt
│   │   │   ├── lib/
│   │   │   │   ├── annotations-20.1.0.jar
│   │   │   │   ├── ant-1.10.11.jar
│   │   │   │   ├── ant-antlr-1.10.12.jar
│   │   │   │   ├── ant-junit-1.10.12.jar
│   │   │   │   ├── ant-launcher-1.10.11.jar
│   │   │   │   ├── antlr4-runtime-4.7.2.jar
│   │   │   │   ├── asm-9.3.jar
│   │   │   │   ├── asm-analysis-9.3.jar
│   │   │   │   ├── asm-commons-9.3.jar
│   │   │   │   ├── asm-tree-9.3.jar
│   │   │   │   ├── commons-compress-1.21.jar
│   │   │   │   ├── commons-io-2.11.0.jar
│   │   │   │   ├── commons-lang-2.6.jar
│   │   │   │   ├── failureaccess-1.0.1.jar
│   │   │   │   ├── fastutil-8.5.2-min.jar
│   │   │   │   ├── file-events-0.22-milestone-24.jar
│   │   │   │   ├── file-events-linux-aarch64-0.22-milestone-24.jar
│   │   │   │   ├── file-events-linux-amd64-0.22-milestone-24.jar
│   │   │   │   ├── file-events-osx-aarch64-0.22-milestone-24.jar
│   │   │   │   ├── file-events-osx-amd64-0.22-milestone-24.jar
│   │   │   │   ├── file-events-windows-amd64-0.22-milestone-24.jar
│   │   │   │   ├── file-events-windows-amd64-min-0.22-milestone-24.jar
│   │   │   │   ├── file-events-windows-i386-0.22-milestone-24.jar
│   │   │   │   ├── file-events-windows-i386-min-0.22-milestone-24.jar
│   │   │   │   ├── gradle-api-metadata-7.6.jar
│   │   │   │   ├── gradle-base-annotations-7.6.jar
│   │   │   │   ├── gradle-base-services-7.6.jar
│   │   │   │   ├── gradle-base-services-groovy-7.6.jar
│   │   │   │   ├── gradle-bootstrap-7.6.jar
│   │   │   │   ├── gradle-build-cache-7.6.jar
│   │   │   │   ├── gradle-build-cache-base-7.6.jar
│   │   │   │   ├── gradle-build-cache-packaging-7.6.jar
│   │   │   │   ├── gradle-build-events-7.6.jar
│   │   │   │   ├── gradle-build-operations-7.6.jar
│   │   │   │   ├── gradle-build-option-7.6.jar
│   │   │   │   ├── gradle-cli-7.6.jar
│   │   │   │   ├── gradle-core-7.6.jar
│   │   │   │   ├── gradle-core-api-7.6.jar
│   │   │   │   ├── gradle-enterprise-logging-7.6.jar
│   │   │   │   ├── gradle-enterprise-operations-7.6.jar
│   │   │   │   ├── gradle-enterprise-workers-7.6.jar
│   │   │   │   ├── gradle-execution-7.6.jar
│   │   │   │   ├── gradle-file-collections-7.6.jar
│   │   │   │   ├── gradle-file-temp-7.6.jar
│   │   │   │   ├── gradle-file-watching-7.6.jar
│   │   │   │   ├── gradle-files-7.6.jar
│   │   │   │   ├── gradle-functional-7.6.jar
│   │   │   │   ├── gradle-hashing-7.6.jar
│   │   │   │   ├── gradle-installation-beacon-7.6.jar
│   │   │   │   ├── gradle-jvm-services-7.6.jar
│   │   │   │   ├── gradle-kotlin-dsl-7.6.jar
│   │   │   │   ├── gradle-kotlin-dsl-tooling-models-7.6.jar
│   │   │   │   ├── gradle-launcher-7.6.jar
│   │   │   │   ├── gradle-logging-7.6.jar
│   │   │   │   ├── gradle-logging-api-7.6.jar
│   │   │   │   ├── gradle-messaging-7.6.jar
│   │   │   │   ├── gradle-model-core-7.6.jar
│   │   │   │   ├── gradle-model-groovy-7.6.jar
│   │   │   │   ├── gradle-native-7.6.jar
│   │   │   │   ├── gradle-normalization-java-7.6.jar
│   │   │   │   ├── gradle-persistent-cache-7.6.jar
│   │   │   │   ├── gradle-problems-7.6.jar
│   │   │   │   ├── gradle-process-services-7.6.jar
│   │   │   │   ├── gradle-resources-7.6.jar
│   │   │   │   ├── gradle-runtime-api-info-7.6.jar
│   │   │   │   ├── gradle-snapshots-7.6.jar
│   │   │   │   ├── gradle-tooling-api-7.6.jar
│   │   │   │   ├── gradle-worker-processes-7.6.jar
│   │   │   │   ├── gradle-worker-services-7.6.jar
│   │   │   │   ├── gradle-wrapper-shared-7.6.jar
│   │   │   │   ├── groovy-3.0.13.jar
│   │   │   │   ├── groovy-ant-3.0.13.jar
│   │   │   │   ├── groovy-astbuilder-3.0.13.jar
│   │   │   │   ├── groovy-console-3.0.13.jar
│   │   │   │   ├── groovy-datetime-3.0.13.jar
│   │   │   │   ├── groovy-dateutil-3.0.13.jar
│   │   │   │   ├── groovy-docgenerator-3.0.13.jar
│   │   │   │   ├── groovy-groovydoc-3.0.13.jar
│   │   │   │   ├── groovy-json-3.0.13.jar
│   │   │   │   ├── groovy-nio-3.0.13.jar
│   │   │   │   ├── groovy-sql-3.0.13.jar
│   │   │   │   ├── groovy-swing-3.0.13.jar
│   │   │   │   ├── groovy-templates-3.0.13.jar
│   │   │   │   ├── groovy-test-3.0.13.jar
│   │   │   │   ├── groovy-xml-3.0.13.jar
│   │   │   │   ├── guava-31.1-jre.jar
│   │   │   │   ├── hamcrest-core-1.3.jar
│   │   │   │   ├── jansi-1.18.jar
│   │   │   │   ├── javaparser-core-3.17.0.jar
│   │   │   │   ├── javax.inject-1.jar
│   │   │   │   ├── jcl-over-slf4j-1.7.30.jar
│   │   │   │   ├── jna-5.10.0.jar
│   │   │   │   ├── jsr305-3.0.2.jar
│   │   │   │   ├── jul-to-slf4j-1.7.30.jar
│   │   │   │   ├── junit-4.13.2.jar
│   │   │   │   ├── kotlin-compiler-embeddable-1.7.10.jar
│   │   │   │   ├── kotlin-daemon-embeddable-1.7.10.jar
│   │   │   │   ├── kotlin-reflect-1.7.10.jar
│   │   │   │   ├── kotlin-sam-with-receiver-compiler-plugin-1.7.10.jar
│   │   │   │   ├── kotlin-script-runtime-1.7.10.jar
│   │   │   │   ├── kotlin-scripting-common-1.7.10.jar
│   │   │   │   ├── kotlin-scripting-compiler-embeddable-1.7.10.jar
│   │   │   │   ├── kotlin-scripting-compiler-impl-embeddable-1.7.10.jar
│   │   │   │   ├── kotlin-scripting-jvm-1.7.10.jar
│   │   │   │   ├── kotlin-scripting-jvm-host-1.7.10.jar
│   │   │   │   ├── kotlin-stdlib-1.7.10.jar
│   │   │   │   ├── kotlin-stdlib-common-1.7.10.jar
│   │   │   │   ├── kotlin-stdlib-jdk7-1.7.10.jar
│   │   │   │   ├── kotlin-stdlib-jdk8-1.7.10.jar
│   │   │   │   ├── kotlinx-metadata-jvm-0.5.0.jar
│   │   │   │   ├── kryo-2.24.0.jar
│   │   │   │   ├── log4j-over-slf4j-1.7.30.jar
│   │   │   │   ├── minlog-1.2.jar
│   │   │   │   ├── native-platform-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-freebsd-amd64-libcpp-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-linux-aarch64-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-linux-aarch64-ncurses5-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-linux-aarch64-ncurses6-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-linux-amd64-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-linux-amd64-ncurses5-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-linux-amd64-ncurses6-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-osx-aarch64-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-osx-amd64-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-windows-amd64-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-windows-amd64-min-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-windows-i386-0.22-milestone-24.jar
│   │   │   │   ├── native-platform-windows-i386-min-0.22-milestone-24.jar
│   │   │   │   ├── objenesis-2.6.jar
│   │   │   │   ├── plugins/
│   │   │   │   │   └── ...
│   │   │   │   ├── qdox-1.12.1.jar
│   │   │   │   ├── slf4j-api-1.7.30.jar
│   │   │   │   ├── tomlj-1.0.0.jar
│   │   │   │   ├── trove4j-1.0.20200330.jar
│   │   │   │   └── xml-apis-1.4.01.jar
│   │   │   ├── LICENSE
│   │   │   ├── NOTICE
│   │   │   └── README
│   │   └── gradle-7.6-bin.zip
│   ├── app/
│   │   ├── build.gradle.kts
│   │   ├── proguard-rules.pro
│   │   └── src/
│   │       └── main/
│   │           ├── AndroidManifest.xml
│   │           ├── java/
│   │           │   └── ...
│   │           └── res/
│   │               └── ...
│   ├── build.gradle.kts
│   ├── gradle/
│   │   ├── libs.versions.toml
│   │   └── wrapper/
│   │       ├── gradle-wrapper.jar
│   │       └── gradle-wrapper.properties
│   ├── gradle.properties
│   ├── gradlew
│   ├── gradlew.bat
│   ├── local.properties
│   ├── release-apk/
│   │   ├── PCControlMobile-signed.apk
│   │   ├── PCControlMobile-v1.0.2.apk
│   │   └── PCControlMobile-v1.0.2.apk.idsig
│   └── settings.gradle.kts
├── backend/
│   ├── .env
│   └── app/
│       ├── __init__.py
│       ├── agents/
│       │   └── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── agent_routes.py
│       │   ├── auth_routes.py
│       │   ├── camera.py
│       │   ├── files.py
│       │   ├── mobile_routes.py
│       │   ├── processes.py
│       │   ├── screenshots.py
│       │   ├── server.py
│       │   └── system_routes.py
│       ├── auth.py
│       ├── bot/
│       │   ├── __init__.py
│       │   ├── lang_ru.py
│       │   ├── runner.py
│       │   └── telegram_bot.py
│       ├── config.py
│       ├── database.py
│       ├── main.py
│       ├── models.py
│       ├── schemas.py
│       ├── services/
│       │   ├── agent_service.py
│       │   ├── file_service.py
│       │   ├── log_service.py
│       │   ├── network_service.py
│       │   ├── server_media_service.py
│       │   ├── task_service.py
│       │   └── wol_service.py
│       ├── utils/
│       │   ├── hashing.py
│       │   ├── logging.py
│       │   └── paths.py
│       ├── web/
│       │   └── panel.html
│       └── websocket/
│           └── manager.py
├── backup_2026-04-26_16-25-59/
│   ├── .env.example
│   ├── android-app/
│   │   ├── .codex-tools/
│   │   │   ├── gradle-7.6/
│   │   │   │   ├── bin/
│   │   │   │   │   └── ...
│   │   │   │   ├── init.d/
│   │   │   │   │   └── ...
│   │   │   │   ├── lib/
│   │   │   │   │   └── ...
│   │   │   │   ├── LICENSE
│   │   │   │   ├── NOTICE
│   │   │   │   └── README
│   │   │   └── gradle-7.6-bin.zip
│   │   ├── app/
│   │   │   ├── build.gradle.kts
│   │   │   ├── proguard-rules.pro
│   │   │   └── src/
│   │   │       └── main/
│   │   │           └── ...
│   │   ├── build.gradle.kts
│   │   ├── gradle/
│   │   │   ├── libs.versions.toml
│   │   │   └── wrapper/
│   │   │       ├── gradle-wrapper.jar
│   │   │       └── gradle-wrapper.properties
│   │   ├── gradle.properties
│   │   ├── gradlew
│   │   ├── gradlew.bat
│   │   ├── local.properties
│   │   ├── release-apk/
│   │   │   ├── PCControlMobile-signed.apk
│   │   │   ├── PCControlMobile-v1.0.2.apk
│   │   │   └── PCControlMobile-v1.0.2.apk.idsig
│   │   └── settings.gradle.kts
│   ├── backend/
│   │   ├── .env
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── agents/
│   │       │   └── __init__.py
│   │       ├── api/
│   │       │   ├── __init__.py
│   │       │   ├── agent_routes.py
│   │       │   ├── auth_routes.py
│   │       │   ├── camera.py
│   │       │   ├── files.py
│   │       │   ├── mobile_routes.py
│   │       │   ├── processes.py
│   │       │   ├── screenshots.py
│   │       │   ├── server.py
│   │       │   └── system_routes.py
│   │       ├── auth.py
│   │       ├── bot/
│   │       │   ├── __init__.py
│   │       │   ├── runner.py
│   │       │   └── telegram_bot.py
│   │       ├── config.py
│   │       ├── database.py
│   │       ├── main.py
│   │       ├── models.py
│   │       ├── schemas.py
│   │       ├── services/
│   │       │   ├── agent_service.py
│   │       │   ├── file_service.py
│   │       │   ├── log_service.py
│   │       │   ├── network_service.py
│   │       │   └── task_service.py
│   │       ├── utils/
│   │       │   ├── hashing.py
│   │       │   ├── logging.py
│   │       │   └── paths.py
│   │       ├── web/
│   │       │   └── panel.html
│   │       └── websocket/
│   │           └── manager.py
│   ├── install_ubuntu.sh
│   ├── pc-agent/
│   │   ├── agent.py
│   │   ├── agent_config.example.json
│   │   ├── logs/
│   │   │   └── agent.log
│   │   └── requirements.txt
│   ├── README.md
│   ├── requirements.txt
│   ├── run_agent.bat
│   ├── run_server.bat
│   ├── scripts/
│   │   ├── backup.sh
│   │   ├── logs.sh
│   │   ├── restart.sh
│   │   ├── start.sh
│   │   ├── status.sh
│   │   ├── stop.sh
│   │   └── update.sh
│   └── systemd/
│       ├── pcmanager-bot.service
│       └── pcmanager-server.service
├── config.example.json
├── docs/
│   └── CODEX_DAILY_SERVER_CHECK.md
├── install_ubuntu.sh
├── install_windows.bat
├── MIGRATION_WINDOWS_TO_UBUNTU.md
├── pc-agent/
│   ├── agent.py
│   ├── agent_config.example.json
│   ├── logs/
│   │   └── agent.log
│   └── requirements.txt
├── README.md
├── requirements.txt
├── run_agent.bat
├── run_server.bat
├── scripts/
│   ├── backup.sh
│   ├── install_server_daily_self_check.sh
│   ├── logs.sh
│   ├── restart.sh
│   ├── server_daily_self_check.sh
│   ├── start.sh
│   ├── status.sh
│   ├── stop.sh
│   └── update.sh
├── systemd/
│   ├── pcmanager-bot.service
│   └── pcmanager-server.service
└── TECHNICAL_FILES_REPORT.md
```

## 3. Какие файлы добавлены и какие изменены

Без git history невозможно на 100% доказать авторство каждого файла, поэтому ниже список сформирован по текущей структуре и рабочему контексту миграции.

### Добавленные/оформленные для Linux и обслуживания
- `MIGRATION_WINDOWS_TO_UBUNTU.md`
- `install_ubuntu.sh`
- `scripts/backup.sh`
- `scripts/install_server_daily_self_check.sh`
- `scripts/logs.sh`
- `scripts/restart.sh`
- `scripts/server_daily_self_check.sh`
- `scripts/start.sh`
- `scripts/status.sh`
- `scripts/stop.sh`
- `scripts/update.sh`
- `systemd/pcmanager-bot.service`
- `systemd/pcmanager-server.service`

### Изменённые/доработанные функциональные файлы
- `android-app/.codex-tools/gradle-7.6/LICENSE`
- `android-app/.codex-tools/gradle-7.6/NOTICE`
- `android-app/.codex-tools/gradle-7.6/README`
- `android-app/.codex-tools/gradle-7.6/bin/gradle`
- `android-app/.codex-tools/gradle-7.6/bin/gradle.bat`
- `android-app/.codex-tools/gradle-7.6/init.d/readme.txt`
- `android-app/.codex-tools/gradle-7.6/lib/annotations-20.1.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/ant-antlr-1.10.12.jar`
- `android-app/.codex-tools/gradle-7.6/lib/ant-junit-1.10.12.jar`
- `android-app/.codex-tools/gradle-7.6/lib/ant-launcher-1.10.11.jar`
- `android-app/.codex-tools/gradle-7.6/lib/antlr4-runtime-4.7.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/asm-9.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/asm-analysis-9.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/asm-commons-9.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/asm-tree-9.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/commons-compress-1.21.jar`
- `android-app/.codex-tools/gradle-7.6/lib/commons-io-2.11.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/commons-lang-2.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/failureaccess-1.0.1.jar`
- `android-app/.codex-tools/gradle-7.6/lib/fastutil-8.5.2-min.jar`
- `android-app/.codex-tools/gradle-7.6/lib/file-events-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/file-events-linux-aarch64-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/file-events-linux-amd64-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/file-events-osx-aarch64-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/file-events-osx-amd64-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-amd64-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-amd64-min-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-i386-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-i386-min-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-api-metadata-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-base-annotations-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-base-services-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-base-services-groovy-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-bootstrap-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-build-cache-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-build-cache-base-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-build-cache-packaging-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-build-events-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-build-operations-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-build-option-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-cli-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-core-api-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-enterprise-logging-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-enterprise-operations-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-enterprise-workers-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-execution-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-file-collections-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-file-temp-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-file-watching-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-files-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-functional-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-hashing-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-installation-beacon-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-jvm-services-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-kotlin-dsl-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-kotlin-dsl-tooling-models-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-launcher-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-logging-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-logging-api-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-messaging-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-model-core-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-model-groovy-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-native-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-normalization-java-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-persistent-cache-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-problems-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-process-services-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-resources-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-runtime-api-info-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-snapshots-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-tooling-api-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-worker-processes-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-worker-services-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/gradle-wrapper-shared-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-ant-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-astbuilder-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-console-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-datetime-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-dateutil-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-docgenerator-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-groovydoc-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-json-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-nio-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-sql-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-swing-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-templates-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-test-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/groovy-xml-3.0.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/hamcrest-core-1.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/jansi-1.18.jar`
- `android-app/.codex-tools/gradle-7.6/lib/javaparser-core-3.17.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/javax.inject-1.jar`
- `android-app/.codex-tools/gradle-7.6/lib/jcl-over-slf4j-1.7.30.jar`
- `android-app/.codex-tools/gradle-7.6/lib/jna-5.10.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/jsr305-3.0.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/jul-to-slf4j-1.7.30.jar`
- `android-app/.codex-tools/gradle-7.6/lib/junit-4.13.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-daemon-embeddable-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-sam-with-receiver-compiler-plugin-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-script-runtime-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-common-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-compiler-embeddable-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-compiler-impl-embeddable-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-jvm-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-jvm-host-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-common-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-jdk7-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-jdk8-1.7.10.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kotlinx-metadata-jvm-0.5.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/kryo-2.24.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/log4j-over-slf4j-1.7.30.jar`
- `android-app/.codex-tools/gradle-7.6/lib/minlog-1.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-freebsd-amd64-libcpp-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-aarch64-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-aarch64-ncurses5-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-aarch64-ncurses6-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-amd64-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-amd64-ncurses5-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-amd64-ncurses6-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-osx-aarch64-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-osx-amd64-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-amd64-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-amd64-min-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-i386-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-i386-min-0.22-milestone-24.jar`
- `android-app/.codex-tools/gradle-7.6/lib/objenesis-2.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-core-1.11.948.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-kms-1.11.948.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-s3-1.11.948.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-sts-1.11.948.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/bcpg-jdk15on-1.68.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/bcpkix-jdk15on-1.68.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/bsh-2.0b6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/capsule-0.6.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/commons-codec-1.15.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/dd-plist-1.21.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/google-api-client-1.34.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/google-api-services-storage-v1-rev20220705-1.32.1.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/google-http-client-1.42.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/google-http-client-apache-v2-1.42.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/google-http-client-gson-1.42.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/google-oauth-client-1.34.1.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-antlr-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-build-cache-http-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-build-init-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-build-profile-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-code-quality-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-composite-builds-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-configuration-cache-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-diagnostics-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ear-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-enterprise-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ide-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ide-native-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ivy-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-jacoco-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-java-compiler-plugin-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-kotlin-dsl-provider-plugins-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-kotlin-dsl-tooling-builders-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-groovy-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-java-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-jvm-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-native-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-maven-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-platform-base-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-platform-jvm-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-platform-native-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-plugin-development-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-plugin-use-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-plugins-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-publish-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-reporting-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-gcs-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-http-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-s3-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-sftp-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-scala-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-security-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-signing-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-test-kit-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-base-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-junit-platform-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-jvm-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-native-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-tooling-api-builders-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-tooling-native-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-version-control-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-workers-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-wrapper-7.6.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/grpc-context-1.27.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/gson-2.8.9.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/httpclient-4.5.13.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/httpcore-4.4.14.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/ion-java-1.0.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/ivy-2.3.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jackson-annotations-2.13.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jackson-core-2.13.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jackson-databind-2.13.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jakarta.activation-2.0.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jakarta.xml.bind-api-3.0.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jatl-0.2.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jaxb-core-3.0.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jaxb-impl-3.0.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jcifs-1.3.17.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jcommander-1.78.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jmespath-java-1.11.948.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/joda-time-2.10.4.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jsch-0.1.55.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jsoup-1.15.1.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/junit-platform-commons-1.8.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/junit-platform-engine-1.8.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/junit-platform-launcher-1.8.2.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/jzlib-1.1.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-builder-support-3.6.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-model-3.6.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-repository-metadata-3.6.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-settings-3.6.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-settings-builder-3.6.3.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/opencensus-api-0.31.1.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/opencensus-contrib-http-util-0.31.1.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/opentest4j-1.2.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-cipher-1.7.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-interpolation-1.26.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-sec-dispatcher-1.4.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-utils-3.3.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/snakeyaml-1.32.jar`
- `android-app/.codex-tools/gradle-7.6/lib/plugins/testng-6.3.1.jar`
- `android-app/.codex-tools/gradle-7.6/lib/qdox-1.12.1.jar`
- `android-app/.codex-tools/gradle-7.6/lib/slf4j-api-1.7.30.jar`
- `android-app/.codex-tools/gradle-7.6/lib/tomlj-1.0.0.jar`
- `android-app/.codex-tools/gradle-7.6/lib/trove4j-1.0.20200330.jar`
- `android-app/.codex-tools/gradle-7.6/lib/xml-apis-1.4.01.jar`
- `android-app/app/build.gradle.kts`
- `android-app/app/proguard-rules.pro`
- `android-app/app/src/main/AndroidManifest.xml`
- `android-app/app/src/main/java/com/example/pccontrolmobile/MainActivity.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/app/AppContainer.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/app/PcControlMobileApp.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/app/SimpleViewModelFactory.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/core/designsystem/theme/Color.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/core/designsystem/theme/Theme.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/core/designsystem/theme/Type.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/core/network/ApiClientFactory.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/core/network/ApiConfig.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/core/network/ApiService.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/core/ui/CommonComponents.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/core/ui/Formatters.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/AppDatabase.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/SettingsDataStore.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/dao/Daos.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/entity/Entities.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/data/remote/api/PcControlApi.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/data/remote/dto/Dtos.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/data/remote/ws/RealtimeGateway.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/data/repository/PcControlRepository.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/data/repository/PcControlRepositoryImpl.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/domain/model/Models.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/feature/agents/AgentsScreen.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/feature/chat/ChatScreen.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/feature/control/ControlScreen.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/feature/dashboard/DashboardScreen.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/feature/files/FilesScreen.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/feature/logs/LogsScreen.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/feature/monitor/MonitorScreen.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/feature/optimizer/OptimizerScreen.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/feature/screen/ScreenRoute.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/feature/settings/SettingsScreen.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/feature/tasks/TasksScreen.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/navigation/PcControlNavHost.kt`
- `android-app/app/src/main/java/com/example/pccontrolmobile/navigation/TopLevelDestination.kt`
- `android-app/app/src/main/res/drawable/ic_launcher_foreground.xml`
- `android-app/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml`
- `android-app/app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml`
- `android-app/app/src/main/res/values/strings.xml`
- `android-app/app/src/main/res/values/themes.xml`
- `android-app/app/src/main/res/xml/network_security_config.xml`
- `android-app/build.gradle.kts`
- `android-app/gradle.properties`
- `android-app/gradle/libs.versions.toml`
- `android-app/gradle/wrapper/gradle-wrapper.jar`
- `android-app/gradle/wrapper/gradle-wrapper.properties`
- `android-app/gradlew`
- `android-app/gradlew.bat`
- `android-app/local.properties`
- `android-app/release-apk/PCControlMobile-v1.0.2.apk.idsig`
- `android-app/settings.gradle.kts`
- `backend/app/api/__init__.py`
- `backend/app/api/agent_routes.py`
- `backend/app/api/auth_routes.py`
- `backend/app/api/camera.py`
- `backend/app/api/files.py`
- `backend/app/api/mobile_routes.py`
- `backend/app/api/processes.py`
- `backend/app/api/screenshots.py`
- `backend/app/api/server.py`
- `backend/app/api/system_routes.py`
- `backend/app/bot/__init__.py`
- `backend/app/bot/lang_ru.py`

## 4. Подробный разбор важных файлов

### `.env.example`

**Файл:** `.env.example`
**Путь:** `.env.example`

**Назначение:** Шаблон переменных окружения без реальных токенов и ключей.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Секреты и флаги вынесены в конфигурацию, реальные значения не должны храниться в коде.

**Какую проблему решает:**
- Решает риск хардкода токенов, IP, access key и feature flags.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/bin/gradle`

**Файл:** `gradle`
**Путь:** `android-app/.codex-tools/gradle-7.6/bin/gradle`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/bin/gradle.bat`

**Файл:** `gradle.bat`
**Путь:** `android-app/.codex-tools/gradle-7.6/bin/gradle.bat`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Требует Windows cmd/PowerShell и установленный Python, если внутри вызывается python.

**Как проверить:**
- Запуск на Windows: `android-app/.codex-tools/gradle-7.6/bin/gradle.bat`

### `android-app/.codex-tools/gradle-7.6/init.d/readme.txt`

**Файл:** `readme.txt`
**Путь:** `android-app/.codex-tools/gradle-7.6/init.d/readme.txt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/annotations-20.1.0.jar`

**Файл:** `annotations-20.1.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/annotations-20.1.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/ant-antlr-1.10.12.jar`

**Файл:** `ant-antlr-1.10.12.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/ant-antlr-1.10.12.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/ant-junit-1.10.12.jar`

**Файл:** `ant-junit-1.10.12.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/ant-junit-1.10.12.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/ant-launcher-1.10.11.jar`

**Файл:** `ant-launcher-1.10.11.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/ant-launcher-1.10.11.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/antlr4-runtime-4.7.2.jar`

**Файл:** `antlr4-runtime-4.7.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/antlr4-runtime-4.7.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/asm-9.3.jar`

**Файл:** `asm-9.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/asm-9.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/asm-analysis-9.3.jar`

**Файл:** `asm-analysis-9.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/asm-analysis-9.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/asm-commons-9.3.jar`

**Файл:** `asm-commons-9.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/asm-commons-9.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/asm-tree-9.3.jar`

**Файл:** `asm-tree-9.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/asm-tree-9.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/commons-compress-1.21.jar`

**Файл:** `commons-compress-1.21.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/commons-compress-1.21.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/commons-io-2.11.0.jar`

**Файл:** `commons-io-2.11.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/commons-io-2.11.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/commons-lang-2.6.jar`

**Файл:** `commons-lang-2.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/commons-lang-2.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/failureaccess-1.0.1.jar`

**Файл:** `failureaccess-1.0.1.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/failureaccess-1.0.1.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/fastutil-8.5.2-min.jar`

**Файл:** `fastutil-8.5.2-min.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/fastutil-8.5.2-min.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/file-events-0.22-milestone-24.jar`

**Файл:** `file-events-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/file-events-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/file-events-linux-aarch64-0.22-milestone-24.jar`

**Файл:** `file-events-linux-aarch64-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/file-events-linux-aarch64-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/file-events-linux-amd64-0.22-milestone-24.jar`

**Файл:** `file-events-linux-amd64-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/file-events-linux-amd64-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/file-events-osx-aarch64-0.22-milestone-24.jar`

**Файл:** `file-events-osx-aarch64-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/file-events-osx-aarch64-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/file-events-osx-amd64-0.22-milestone-24.jar`

**Файл:** `file-events-osx-amd64-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/file-events-osx-amd64-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-amd64-0.22-milestone-24.jar`

**Файл:** `file-events-windows-amd64-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-amd64-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-amd64-min-0.22-milestone-24.jar`

**Файл:** `file-events-windows-amd64-min-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-amd64-min-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-i386-0.22-milestone-24.jar`

**Файл:** `file-events-windows-i386-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-i386-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-i386-min-0.22-milestone-24.jar`

**Файл:** `file-events-windows-i386-min-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/file-events-windows-i386-min-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-api-metadata-7.6.jar`

**Файл:** `gradle-api-metadata-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-api-metadata-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-base-annotations-7.6.jar`

**Файл:** `gradle-base-annotations-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-base-annotations-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-base-services-7.6.jar`

**Файл:** `gradle-base-services-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-base-services-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-base-services-groovy-7.6.jar`

**Файл:** `gradle-base-services-groovy-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-base-services-groovy-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-bootstrap-7.6.jar`

**Файл:** `gradle-bootstrap-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-bootstrap-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-build-cache-7.6.jar`

**Файл:** `gradle-build-cache-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-build-cache-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-build-cache-base-7.6.jar`

**Файл:** `gradle-build-cache-base-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-build-cache-base-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-build-cache-packaging-7.6.jar`

**Файл:** `gradle-build-cache-packaging-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-build-cache-packaging-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-build-events-7.6.jar`

**Файл:** `gradle-build-events-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-build-events-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-build-operations-7.6.jar`

**Файл:** `gradle-build-operations-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-build-operations-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-build-option-7.6.jar`

**Файл:** `gradle-build-option-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-build-option-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-cli-7.6.jar`

**Файл:** `gradle-cli-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-cli-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-core-api-7.6.jar`

**Файл:** `gradle-core-api-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-core-api-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-enterprise-logging-7.6.jar`

**Файл:** `gradle-enterprise-logging-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-enterprise-logging-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-enterprise-operations-7.6.jar`

**Файл:** `gradle-enterprise-operations-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-enterprise-operations-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-enterprise-workers-7.6.jar`

**Файл:** `gradle-enterprise-workers-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-enterprise-workers-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-execution-7.6.jar`

**Файл:** `gradle-execution-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-execution-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-file-collections-7.6.jar`

**Файл:** `gradle-file-collections-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-file-collections-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-file-temp-7.6.jar`

**Файл:** `gradle-file-temp-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-file-temp-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-file-watching-7.6.jar`

**Файл:** `gradle-file-watching-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-file-watching-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-files-7.6.jar`

**Файл:** `gradle-files-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-files-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-functional-7.6.jar`

**Файл:** `gradle-functional-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-functional-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-hashing-7.6.jar`

**Файл:** `gradle-hashing-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-hashing-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-installation-beacon-7.6.jar`

**Файл:** `gradle-installation-beacon-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-installation-beacon-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-jvm-services-7.6.jar`

**Файл:** `gradle-jvm-services-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-jvm-services-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-kotlin-dsl-7.6.jar`

**Файл:** `gradle-kotlin-dsl-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-kotlin-dsl-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-kotlin-dsl-tooling-models-7.6.jar`

**Файл:** `gradle-kotlin-dsl-tooling-models-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-kotlin-dsl-tooling-models-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-launcher-7.6.jar`

**Файл:** `gradle-launcher-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-launcher-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-logging-7.6.jar`

**Файл:** `gradle-logging-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-logging-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-logging-api-7.6.jar`

**Файл:** `gradle-logging-api-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-logging-api-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-messaging-7.6.jar`

**Файл:** `gradle-messaging-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-messaging-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-model-core-7.6.jar`

**Файл:** `gradle-model-core-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-model-core-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-model-groovy-7.6.jar`

**Файл:** `gradle-model-groovy-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-model-groovy-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-native-7.6.jar`

**Файл:** `gradle-native-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-native-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-normalization-java-7.6.jar`

**Файл:** `gradle-normalization-java-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-normalization-java-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-persistent-cache-7.6.jar`

**Файл:** `gradle-persistent-cache-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-persistent-cache-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-problems-7.6.jar`

**Файл:** `gradle-problems-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-problems-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-process-services-7.6.jar`

**Файл:** `gradle-process-services-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-process-services-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-resources-7.6.jar`

**Файл:** `gradle-resources-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-resources-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-runtime-api-info-7.6.jar`

**Файл:** `gradle-runtime-api-info-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-runtime-api-info-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-snapshots-7.6.jar`

**Файл:** `gradle-snapshots-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-snapshots-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-tooling-api-7.6.jar`

**Файл:** `gradle-tooling-api-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-tooling-api-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-worker-processes-7.6.jar`

**Файл:** `gradle-worker-processes-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-worker-processes-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-worker-services-7.6.jar`

**Файл:** `gradle-worker-services-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-worker-services-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/gradle-wrapper-shared-7.6.jar`

**Файл:** `gradle-wrapper-shared-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/gradle-wrapper-shared-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-ant-3.0.13.jar`

**Файл:** `groovy-ant-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-ant-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-astbuilder-3.0.13.jar`

**Файл:** `groovy-astbuilder-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-astbuilder-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-console-3.0.13.jar`

**Файл:** `groovy-console-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-console-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-datetime-3.0.13.jar`

**Файл:** `groovy-datetime-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-datetime-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-dateutil-3.0.13.jar`

**Файл:** `groovy-dateutil-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-dateutil-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-docgenerator-3.0.13.jar`

**Файл:** `groovy-docgenerator-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-docgenerator-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-groovydoc-3.0.13.jar`

**Файл:** `groovy-groovydoc-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-groovydoc-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-json-3.0.13.jar`

**Файл:** `groovy-json-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-json-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-nio-3.0.13.jar`

**Файл:** `groovy-nio-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-nio-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-sql-3.0.13.jar`

**Файл:** `groovy-sql-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-sql-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-swing-3.0.13.jar`

**Файл:** `groovy-swing-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-swing-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-templates-3.0.13.jar`

**Файл:** `groovy-templates-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-templates-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-test-3.0.13.jar`

**Файл:** `groovy-test-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-test-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/groovy-xml-3.0.13.jar`

**Файл:** `groovy-xml-3.0.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/groovy-xml-3.0.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/hamcrest-core-1.3.jar`

**Файл:** `hamcrest-core-1.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/hamcrest-core-1.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/jansi-1.18.jar`

**Файл:** `jansi-1.18.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/jansi-1.18.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/javaparser-core-3.17.0.jar`

**Файл:** `javaparser-core-3.17.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/javaparser-core-3.17.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/javax.inject-1.jar`

**Файл:** `javax.inject-1.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/javax.inject-1.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/jcl-over-slf4j-1.7.30.jar`

**Файл:** `jcl-over-slf4j-1.7.30.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/jcl-over-slf4j-1.7.30.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/jna-5.10.0.jar`

**Файл:** `jna-5.10.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/jna-5.10.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/jsr305-3.0.2.jar`

**Файл:** `jsr305-3.0.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/jsr305-3.0.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/jul-to-slf4j-1.7.30.jar`

**Файл:** `jul-to-slf4j-1.7.30.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/jul-to-slf4j-1.7.30.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/junit-4.13.2.jar`

**Файл:** `junit-4.13.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/junit-4.13.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-daemon-embeddable-1.7.10.jar`

**Файл:** `kotlin-daemon-embeddable-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-daemon-embeddable-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-sam-with-receiver-compiler-plugin-1.7.10.jar`

**Файл:** `kotlin-sam-with-receiver-compiler-plugin-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-sam-with-receiver-compiler-plugin-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-script-runtime-1.7.10.jar`

**Файл:** `kotlin-script-runtime-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-script-runtime-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-common-1.7.10.jar`

**Файл:** `kotlin-scripting-common-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-common-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-compiler-embeddable-1.7.10.jar`

**Файл:** `kotlin-scripting-compiler-embeddable-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-compiler-embeddable-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-compiler-impl-embeddable-1.7.10.jar`

**Файл:** `kotlin-scripting-compiler-impl-embeddable-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-compiler-impl-embeddable-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-jvm-1.7.10.jar`

**Файл:** `kotlin-scripting-jvm-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-jvm-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-jvm-host-1.7.10.jar`

**Файл:** `kotlin-scripting-jvm-host-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-scripting-jvm-host-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-1.7.10.jar`

**Файл:** `kotlin-stdlib-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-common-1.7.10.jar`

**Файл:** `kotlin-stdlib-common-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-common-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-jdk7-1.7.10.jar`

**Файл:** `kotlin-stdlib-jdk7-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-jdk7-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-jdk8-1.7.10.jar`

**Файл:** `kotlin-stdlib-jdk8-1.7.10.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlin-stdlib-jdk8-1.7.10.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kotlinx-metadata-jvm-0.5.0.jar`

**Файл:** `kotlinx-metadata-jvm-0.5.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kotlinx-metadata-jvm-0.5.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/kryo-2.24.0.jar`

**Файл:** `kryo-2.24.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/kryo-2.24.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/log4j-over-slf4j-1.7.30.jar`

**Файл:** `log4j-over-slf4j-1.7.30.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/log4j-over-slf4j-1.7.30.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/minlog-1.2.jar`

**Файл:** `minlog-1.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/minlog-1.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-0.22-milestone-24.jar`

**Файл:** `native-platform-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-freebsd-amd64-libcpp-0.22-milestone-24.jar`

**Файл:** `native-platform-freebsd-amd64-libcpp-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-freebsd-amd64-libcpp-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-aarch64-0.22-milestone-24.jar`

**Файл:** `native-platform-linux-aarch64-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-aarch64-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-aarch64-ncurses5-0.22-milestone-24.jar`

**Файл:** `native-platform-linux-aarch64-ncurses5-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-aarch64-ncurses5-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-aarch64-ncurses6-0.22-milestone-24.jar`

**Файл:** `native-platform-linux-aarch64-ncurses6-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-aarch64-ncurses6-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-amd64-0.22-milestone-24.jar`

**Файл:** `native-platform-linux-amd64-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-amd64-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-amd64-ncurses5-0.22-milestone-24.jar`

**Файл:** `native-platform-linux-amd64-ncurses5-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-amd64-ncurses5-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-amd64-ncurses6-0.22-milestone-24.jar`

**Файл:** `native-platform-linux-amd64-ncurses6-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-linux-amd64-ncurses6-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-osx-aarch64-0.22-milestone-24.jar`

**Файл:** `native-platform-osx-aarch64-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-osx-aarch64-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-osx-amd64-0.22-milestone-24.jar`

**Файл:** `native-platform-osx-amd64-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-osx-amd64-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-amd64-0.22-milestone-24.jar`

**Файл:** `native-platform-windows-amd64-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-amd64-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-amd64-min-0.22-milestone-24.jar`

**Файл:** `native-platform-windows-amd64-min-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-amd64-min-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-i386-0.22-milestone-24.jar`

**Файл:** `native-platform-windows-i386-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-i386-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-i386-min-0.22-milestone-24.jar`

**Файл:** `native-platform-windows-i386-min-0.22-milestone-24.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/native-platform-windows-i386-min-0.22-milestone-24.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/objenesis-2.6.jar`

**Файл:** `objenesis-2.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/objenesis-2.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-core-1.11.948.jar`

**Файл:** `aws-java-sdk-core-1.11.948.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-core-1.11.948.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-kms-1.11.948.jar`

**Файл:** `aws-java-sdk-kms-1.11.948.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-kms-1.11.948.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-s3-1.11.948.jar`

**Файл:** `aws-java-sdk-s3-1.11.948.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-s3-1.11.948.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-sts-1.11.948.jar`

**Файл:** `aws-java-sdk-sts-1.11.948.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/aws-java-sdk-sts-1.11.948.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/bcpg-jdk15on-1.68.jar`

**Файл:** `bcpg-jdk15on-1.68.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/bcpg-jdk15on-1.68.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/bcpkix-jdk15on-1.68.jar`

**Файл:** `bcpkix-jdk15on-1.68.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/bcpkix-jdk15on-1.68.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/bsh-2.0b6.jar`

**Файл:** `bsh-2.0b6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/bsh-2.0b6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/capsule-0.6.3.jar`

**Файл:** `capsule-0.6.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/capsule-0.6.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/commons-codec-1.15.jar`

**Файл:** `commons-codec-1.15.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/commons-codec-1.15.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/dd-plist-1.21.jar`

**Файл:** `dd-plist-1.21.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/dd-plist-1.21.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/google-api-client-1.34.0.jar`

**Файл:** `google-api-client-1.34.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/google-api-client-1.34.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/google-api-services-storage-v1-rev20220705-1.32.1.jar`

**Файл:** `google-api-services-storage-v1-rev20220705-1.32.1.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/google-api-services-storage-v1-rev20220705-1.32.1.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/google-http-client-1.42.2.jar`

**Файл:** `google-http-client-1.42.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/google-http-client-1.42.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/google-http-client-apache-v2-1.42.2.jar`

**Файл:** `google-http-client-apache-v2-1.42.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/google-http-client-apache-v2-1.42.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/google-http-client-gson-1.42.2.jar`

**Файл:** `google-http-client-gson-1.42.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/google-http-client-gson-1.42.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/google-oauth-client-1.34.1.jar`

**Файл:** `google-oauth-client-1.34.1.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/google-oauth-client-1.34.1.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-antlr-7.6.jar`

**Файл:** `gradle-antlr-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-antlr-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-build-cache-http-7.6.jar`

**Файл:** `gradle-build-cache-http-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-build-cache-http-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-build-init-7.6.jar`

**Файл:** `gradle-build-init-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-build-init-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-build-profile-7.6.jar`

**Файл:** `gradle-build-profile-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-build-profile-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-code-quality-7.6.jar`

**Файл:** `gradle-code-quality-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-code-quality-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-composite-builds-7.6.jar`

**Файл:** `gradle-composite-builds-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-composite-builds-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-configuration-cache-7.6.jar`

**Файл:** `gradle-configuration-cache-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-configuration-cache-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-diagnostics-7.6.jar`

**Файл:** `gradle-diagnostics-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-diagnostics-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ear-7.6.jar`

**Файл:** `gradle-ear-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ear-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-enterprise-7.6.jar`

**Файл:** `gradle-enterprise-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-enterprise-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ide-7.6.jar`

**Файл:** `gradle-ide-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ide-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ide-native-7.6.jar`

**Файл:** `gradle-ide-native-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ide-native-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ivy-7.6.jar`

**Файл:** `gradle-ivy-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-ivy-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-jacoco-7.6.jar`

**Файл:** `gradle-jacoco-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-jacoco-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-java-compiler-plugin-7.6.jar`

**Файл:** `gradle-java-compiler-plugin-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-java-compiler-plugin-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-kotlin-dsl-provider-plugins-7.6.jar`

**Файл:** `gradle-kotlin-dsl-provider-plugins-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-kotlin-dsl-provider-plugins-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-kotlin-dsl-tooling-builders-7.6.jar`

**Файл:** `gradle-kotlin-dsl-tooling-builders-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-kotlin-dsl-tooling-builders-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-groovy-7.6.jar`

**Файл:** `gradle-language-groovy-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-groovy-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-java-7.6.jar`

**Файл:** `gradle-language-java-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-java-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-jvm-7.6.jar`

**Файл:** `gradle-language-jvm-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-jvm-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-native-7.6.jar`

**Файл:** `gradle-language-native-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-language-native-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-maven-7.6.jar`

**Файл:** `gradle-maven-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-maven-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-platform-base-7.6.jar`

**Файл:** `gradle-platform-base-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-platform-base-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-platform-jvm-7.6.jar`

**Файл:** `gradle-platform-jvm-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-platform-jvm-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-platform-native-7.6.jar`

**Файл:** `gradle-platform-native-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-platform-native-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-plugin-development-7.6.jar`

**Файл:** `gradle-plugin-development-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-plugin-development-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-plugin-use-7.6.jar`

**Файл:** `gradle-plugin-use-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-plugin-use-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-plugins-7.6.jar`

**Файл:** `gradle-plugins-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-plugins-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-publish-7.6.jar`

**Файл:** `gradle-publish-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-publish-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-reporting-7.6.jar`

**Файл:** `gradle-reporting-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-reporting-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-gcs-7.6.jar`

**Файл:** `gradle-resources-gcs-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-gcs-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-http-7.6.jar`

**Файл:** `gradle-resources-http-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-http-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-s3-7.6.jar`

**Файл:** `gradle-resources-s3-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-s3-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-sftp-7.6.jar`

**Файл:** `gradle-resources-sftp-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-resources-sftp-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-scala-7.6.jar`

**Файл:** `gradle-scala-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-scala-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-security-7.6.jar`

**Файл:** `gradle-security-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-security-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-signing-7.6.jar`

**Файл:** `gradle-signing-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-signing-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-test-kit-7.6.jar`

**Файл:** `gradle-test-kit-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-test-kit-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-base-7.6.jar`

**Файл:** `gradle-testing-base-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-base-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-junit-platform-7.6.jar`

**Файл:** `gradle-testing-junit-platform-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-junit-platform-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-jvm-7.6.jar`

**Файл:** `gradle-testing-jvm-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-jvm-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-native-7.6.jar`

**Файл:** `gradle-testing-native-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-testing-native-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-tooling-api-builders-7.6.jar`

**Файл:** `gradle-tooling-api-builders-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-tooling-api-builders-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-tooling-native-7.6.jar`

**Файл:** `gradle-tooling-native-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-tooling-native-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-version-control-7.6.jar`

**Файл:** `gradle-version-control-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-version-control-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-workers-7.6.jar`

**Файл:** `gradle-workers-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-workers-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-wrapper-7.6.jar`

**Файл:** `gradle-wrapper-7.6.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gradle-wrapper-7.6.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/grpc-context-1.27.2.jar`

**Файл:** `grpc-context-1.27.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/grpc-context-1.27.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/gson-2.8.9.jar`

**Файл:** `gson-2.8.9.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/gson-2.8.9.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/httpclient-4.5.13.jar`

**Файл:** `httpclient-4.5.13.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/httpclient-4.5.13.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/httpcore-4.4.14.jar`

**Файл:** `httpcore-4.4.14.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/httpcore-4.4.14.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/ion-java-1.0.2.jar`

**Файл:** `ion-java-1.0.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/ion-java-1.0.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/ivy-2.3.0.jar`

**Файл:** `ivy-2.3.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/ivy-2.3.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jackson-annotations-2.13.3.jar`

**Файл:** `jackson-annotations-2.13.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jackson-annotations-2.13.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jackson-core-2.13.3.jar`

**Файл:** `jackson-core-2.13.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jackson-core-2.13.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jackson-databind-2.13.3.jar`

**Файл:** `jackson-databind-2.13.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jackson-databind-2.13.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jakarta.activation-2.0.0.jar`

**Файл:** `jakarta.activation-2.0.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jakarta.activation-2.0.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jakarta.xml.bind-api-3.0.0.jar`

**Файл:** `jakarta.xml.bind-api-3.0.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jakarta.xml.bind-api-3.0.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jatl-0.2.3.jar`

**Файл:** `jatl-0.2.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jatl-0.2.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jaxb-core-3.0.0.jar`

**Файл:** `jaxb-core-3.0.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jaxb-core-3.0.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jaxb-impl-3.0.0.jar`

**Файл:** `jaxb-impl-3.0.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jaxb-impl-3.0.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jcifs-1.3.17.jar`

**Файл:** `jcifs-1.3.17.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jcifs-1.3.17.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jcommander-1.78.jar`

**Файл:** `jcommander-1.78.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jcommander-1.78.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jmespath-java-1.11.948.jar`

**Файл:** `jmespath-java-1.11.948.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jmespath-java-1.11.948.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/joda-time-2.10.4.jar`

**Файл:** `joda-time-2.10.4.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/joda-time-2.10.4.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jsch-0.1.55.jar`

**Файл:** `jsch-0.1.55.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jsch-0.1.55.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jsoup-1.15.1.jar`

**Файл:** `jsoup-1.15.1.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jsoup-1.15.1.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/junit-platform-commons-1.8.2.jar`

**Файл:** `junit-platform-commons-1.8.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/junit-platform-commons-1.8.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/junit-platform-engine-1.8.2.jar`

**Файл:** `junit-platform-engine-1.8.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/junit-platform-engine-1.8.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/junit-platform-launcher-1.8.2.jar`

**Файл:** `junit-platform-launcher-1.8.2.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/junit-platform-launcher-1.8.2.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/jzlib-1.1.3.jar`

**Файл:** `jzlib-1.1.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/jzlib-1.1.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-builder-support-3.6.3.jar`

**Файл:** `maven-builder-support-3.6.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-builder-support-3.6.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-model-3.6.3.jar`

**Файл:** `maven-model-3.6.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-model-3.6.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-repository-metadata-3.6.3.jar`

**Файл:** `maven-repository-metadata-3.6.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-repository-metadata-3.6.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-settings-3.6.3.jar`

**Файл:** `maven-settings-3.6.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-settings-3.6.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-settings-builder-3.6.3.jar`

**Файл:** `maven-settings-builder-3.6.3.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/maven-settings-builder-3.6.3.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/opencensus-api-0.31.1.jar`

**Файл:** `opencensus-api-0.31.1.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/opencensus-api-0.31.1.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/opencensus-contrib-http-util-0.31.1.jar`

**Файл:** `opencensus-contrib-http-util-0.31.1.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/opencensus-contrib-http-util-0.31.1.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/opentest4j-1.2.0.jar`

**Файл:** `opentest4j-1.2.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/opentest4j-1.2.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-cipher-1.7.jar`

**Файл:** `plexus-cipher-1.7.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-cipher-1.7.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-interpolation-1.26.jar`

**Файл:** `plexus-interpolation-1.26.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-interpolation-1.26.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-sec-dispatcher-1.4.jar`

**Файл:** `plexus-sec-dispatcher-1.4.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-sec-dispatcher-1.4.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-utils-3.3.0.jar`

**Файл:** `plexus-utils-3.3.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/plexus-utils-3.3.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/snakeyaml-1.32.jar`

**Файл:** `snakeyaml-1.32.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/snakeyaml-1.32.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/plugins/testng-6.3.1.jar`

**Файл:** `testng-6.3.1.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/plugins/testng-6.3.1.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/qdox-1.12.1.jar`

**Файл:** `qdox-1.12.1.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/qdox-1.12.1.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/slf4j-api-1.7.30.jar`

**Файл:** `slf4j-api-1.7.30.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/slf4j-api-1.7.30.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/tomlj-1.0.0.jar`

**Файл:** `tomlj-1.0.0.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/tomlj-1.0.0.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/trove4j-1.0.20200330.jar`

**Файл:** `trove4j-1.0.20200330.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/trove4j-1.0.20200330.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/lib/xml-apis-1.4.01.jar`

**Файл:** `xml-apis-1.4.01.jar`
**Путь:** `android-app/.codex-tools/gradle-7.6/lib/xml-apis-1.4.01.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/LICENSE`

**Файл:** `LICENSE`
**Путь:** `android-app/.codex-tools/gradle-7.6/LICENSE`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/NOTICE`

**Файл:** `NOTICE`
**Путь:** `android-app/.codex-tools/gradle-7.6/NOTICE`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/.codex-tools/gradle-7.6/README`

**Файл:** `README`
**Путь:** `android-app/.codex-tools/gradle-7.6/README`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/app/build.gradle.kts`

**Файл:** `build.gradle.kts`
**Путь:** `android-app/app/build.gradle.kts`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/app/proguard-rules.pro`

**Файл:** `proguard-rules.pro`
**Путь:** `android-app/app/proguard-rules.pro`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/app/src/main/AndroidManifest.xml`

**Файл:** `AndroidManifest.xml`
**Путь:** `android-app/app/src/main/AndroidManifest.xml`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/app/src/main/java/com/example/pccontrolmobile/app/AppContainer.kt`

**Файл:** `AppContainer.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/app/AppContainer.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `AppContainer`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/app/PcControlMobileApp.kt`

**Файл:** `PcControlMobileApp.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/app/PcControlMobileApp.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `PcControlMobileApp`.
- Функции: `onCreate`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/app/SimpleViewModelFactory.kt`

**Файл:** `SimpleViewModelFactory.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/app/SimpleViewModelFactory.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `SimpleViewModelFactory`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/core/designsystem/theme/Color.kt`

**Файл:** `Color.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/core/designsystem/theme/Color.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/core/designsystem/theme/Theme.kt`

**Файл:** `Theme.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/core/designsystem/theme/Theme.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Функции: `PcControlMobileTheme`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/core/designsystem/theme/Type.kt`

**Файл:** `Type.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/core/designsystem/theme/Type.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/core/network/ApiClientFactory.kt`

**Файл:** `ApiClientFactory.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/core/network/ApiClientFactory.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `ApiClientFactory`.
- Функции: `create`, `httpClient`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/core/network/ApiConfig.kt`

**Файл:** `ApiConfig.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/core/network/ApiConfig.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `ApiConfig`.
- Функции: `normalizeBaseUrl`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/core/network/ApiService.kt`

**Файл:** `ApiService.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/core/network/ApiService.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `ApiService`.
- Функции: `create`, `httpClient`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/core/ui/CommonComponents.kt`

**Файл:** `CommonComponents.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/core/ui/CommonComponents.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Функции: `DashboardCard`, `MetricCard`, `StatusChip`, `SectionTitle`, `LoadingState`, `ErrorState`, `InlineStatusBanner`, `EmptyState`, `MetricHistoryChart`, `ActionTile`, `LogRow`, `LogsList`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/core/ui/Formatters.kt`

**Файл:** `Formatters.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/core/ui/Formatters.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Функции: `percentText`, `decimalText`, `bytesText`, `formatTime`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/AppDatabase.kt`

**Файл:** `AppDatabase.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/AppDatabase.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `AppDatabase`.
- Функции: `metricsHistoryDao`, `logDao`, `actionHistoryDao`, `create`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/dao/Daos.kt`

**Файл:** `Daos.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/dao/Daos.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `MetricsHistoryDao`, `LogDao`, `ActionHistoryDao`.
- Функции: `observeRecent`, `insert`, `trim`, `observeRecent`, `insertAll`, `clear`, `observeRecent`, `insert`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/entity/Entities.kt`

**Файл:** `Entities.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/entity/Entities.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `MetricsHistoryEntity`, `LogEntity`, `ActionHistoryEntity`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/SettingsDataStore.kt`

**Файл:** `SettingsDataStore.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/data/local/SettingsDataStore.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `SettingsDataStore`, `Keys`.
- Функции: `getSettings`, `updateSettings`, `mapSettings`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/data/remote/api/PcControlApi.kt`

**Файл:** `PcControlApi.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/data/remote/api/PcControlApi.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `PcControlApi`.
- Функции: `login`, `getSystemStatus`, `getSystemMetrics`, `getSystemLogs`, `optimizeQuick`, `optimizeDeep`, `optimizeTemp`, `restartAgent`, `restartPc`, `shutdownPc`, `getFiles`, `getMobileServerInfo`, `getMobileConnectionInfo`, `getFileDetails`, `getMobileAgents`, `getMobileAgent`, `getAgentProcesses`, `refreshAgentProcesses`, `takeAgentScreenshot`, `takeAgentCameraPhoto`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/data/remote/dto/Dtos.kt`

**Файл:** `Dtos.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/data/remote/dto/Dtos.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `StatusDto`, `MetricsDto`, `LogDto`, `ActionResponseDto`, `FileDto`, `ServerInfoDto`, `ChatMessageDto`, `LoginRequestDto`, `LoginResponseDto`, `MobileAgentDto`, `MobileTaskDto`, `MobileTaskCreateDto`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/data/remote/ws/RealtimeGateway.kt`

**Файл:** `RealtimeGateway.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/data/remote/ws/RealtimeGateway.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `RealtimeGateway`.
- Функции: `connect`, `disconnect`, `sendChatMessage`, `connectChat`, `onOpen`, `onMessage`, `onFailure`, `onClosed`, `connectStatus`, `onMessage`, `joinWs`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/data/repository/PcControlRepository.kt`

**Файл:** `PcControlRepository.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/data/repository/PcControlRepository.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `PcControlRepository`.
- Функции: `observeMetricsHistory`, `observeLogs`, `observeActionHistory`, `refreshStatus`, `refreshMetrics`, `refreshLogs`, `loadFiles`, `getFileDetails`, `loadAgents`, `loadTasks`, `createAgentTask`, `cancelTask`, `retryTask`, `quickCleanup`, `deepCleanup`, `tempCleanup`, `restartAgent`, `restartPc`, `shutdownPc`, `loadServerScreen`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/data/repository/PcControlRepositoryImpl.kt`

**Файл:** `PcControlRepositoryImpl.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/data/repository/PcControlRepositoryImpl.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `PcControlRepositoryImpl`.
- Функции: `observeMetricsHistory`, `observeLogs`, `observeActionHistory`, `refreshStatus`, `refreshMetrics`, `refreshLogs`, `loadFiles`, `getFileDetails`, `loadAgents`, `loadTasks`, `createAgentTask`, `cancelTask`, `retryTask`, `quickCleanup`, `deepCleanup`, `tempCleanup`, `restartAgent`, `restartPc`, `shutdownPc`, `loadServerScreen`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/domain/model/Models.kt`

**Файл:** `Models.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/domain/model/Models.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `SystemStatus`, `SystemMetrics`, `LogLevel`, `LogEntry`, `OptimizationType`, `ActionResult`, `OptimizationResult`, `ActionHistoryItem`, `ChatAuthor`, `ChatMessage`, `RemoteFile`, `MobileAgent`, `MobileTask`, `SocketConnectionState`, `AppSettings`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/feature/agents/AgentsScreen.kt`

**Файл:** `AgentsScreen.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/feature/agents/AgentsScreen.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `AgentsUiState`, `AgentsViewModel`.
- Функции: `refresh`, `ping`, `AgentsRoute`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/feature/chat/ChatScreen.kt`

**Файл:** `ChatScreen.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/feature/chat/ChatScreen.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `ChatUiState`, `ChatViewModel`.
- Функции: `updateInput`, `send`, `onCleared`, `ChatRoute`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/feature/control/ControlScreen.kt`

**Файл:** `ControlScreen.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/feature/control/ControlScreen.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `ControlAction`, `ControlUiState`, `ControlViewModel`.
- Функции: `run`, `ControlRoute`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/feature/dashboard/DashboardScreen.kt`

**Файл:** `DashboardScreen.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/feature/dashboard/DashboardScreen.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `DashboardUiState`, `DashboardMetricCard`, `DashboardViewModel`.
- Функции: `refresh`, `DashboardRoute`, `BoxPullRefreshIndicator`, `DashboardScreen`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/feature/files/FilesScreen.kt`

**Файл:** `FilesScreen.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/feature/files/FilesScreen.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `FilesUiState`, `FilesViewModel`.
- Функции: `refresh`, `updateQuery`, `FilesRoute`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/feature/logs/LogsScreen.kt`

**Файл:** `LogsScreen.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/feature/logs/LogsScreen.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `LogsUiState`, `LogsViewModel`.
- Функции: `refresh`, `updateQuery`, `toggleFilter`, `LogsRoute`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/feature/monitor/MonitorScreen.kt`

**Файл:** `MonitorScreen.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/feature/monitor/MonitorScreen.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `MonitorUiState`, `MonitorViewModel`.
- Функции: `refresh`, `MonitorRoute`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/feature/optimizer/OptimizerScreen.kt`

**Файл:** `OptimizerScreen.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/feature/optimizer/OptimizerScreen.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `OptimizerUiState`, `OptimizerViewModel`.
- Функции: `runQuick`, `runDeep`, `runTemp`, `runAction`, `OptimizerRoute`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/feature/screen/ScreenRoute.kt`

**Файл:** `ScreenRoute.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/feature/screen/ScreenRoute.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `ScreenUiState`, `ScreenViewModel`.
- Функции: `refresh`, `setAutoRefresh`, `ScreenRoute`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/feature/settings/SettingsScreen.kt`

**Файл:** `SettingsScreen.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/feature/settings/SettingsScreen.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `SettingsUiState`, `SettingsViewModel`.
- Функции: `updateBaseUrl`, `updateWebSocketUrl`, `updateAccessKey`, `updateRefreshInterval`, `updateNotifications`, `updateDarkMode`, `save`, `testConnection`, `SettingsRoute`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/feature/tasks/TasksScreen.kt`

**Файл:** `TasksScreen.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/feature/tasks/TasksScreen.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `TasksUiState`, `TasksViewModel`.
- Функции: `refresh`, `cancel`, `retry`, `TasksRoute`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/MainActivity.kt`

**Файл:** `MainActivity.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/MainActivity.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `MainActivity`.
- Функции: `onCreate`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/navigation/PcControlNavHost.kt`

**Файл:** `PcControlNavHost.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/navigation/PcControlNavHost.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Функции: `PcControlNavHost`, `routeTitle`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/java/com/example/pccontrolmobile/navigation/TopLevelDestination.kt`

**Файл:** `TopLevelDestination.kt`
**Путь:** `android-app/app/src/main/java/com/example/pccontrolmobile/navigation/TopLevelDestination.kt`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Kotlin-типы: `TopLevelDestination`, `Home`, `Monitor`, `Control`, `Logs`, `Settings`, `ExtraDestination`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от Android Gradle/Kotlin, Compose/Retrofit/DataStore по структуре приложения.

**Как проверить:**
- `cd android-app && ./gradlew assembleDebug`

### `android-app/app/src/main/res/drawable/ic_launcher_foreground.xml`

**Файл:** `ic_launcher_foreground.xml`
**Путь:** `android-app/app/src/main/res/drawable/ic_launcher_foreground.xml`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml`

**Файл:** `ic_launcher.xml`
**Путь:** `android-app/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml`

**Файл:** `ic_launcher_round.xml`
**Путь:** `android-app/app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/app/src/main/res/values/strings.xml`

**Файл:** `strings.xml`
**Путь:** `android-app/app/src/main/res/values/strings.xml`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/app/src/main/res/values/themes.xml`

**Файл:** `themes.xml`
**Путь:** `android-app/app/src/main/res/values/themes.xml`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/app/src/main/res/xml/network_security_config.xml`

**Файл:** `network_security_config.xml`
**Путь:** `android-app/app/src/main/res/xml/network_security_config.xml`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/build.gradle.kts`

**Файл:** `build.gradle.kts`
**Путь:** `android-app/build.gradle.kts`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/gradle/libs.versions.toml`

**Файл:** `libs.versions.toml`
**Путь:** `android-app/gradle/libs.versions.toml`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/gradle/wrapper/gradle-wrapper.jar`

**Файл:** `gradle-wrapper.jar`
**Путь:** `android-app/gradle/wrapper/gradle-wrapper.jar`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/gradle/wrapper/gradle-wrapper.properties`

**Файл:** `gradle-wrapper.properties`
**Путь:** `android-app/gradle/wrapper/gradle-wrapper.properties`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/gradle.properties`

**Файл:** `gradle.properties`
**Путь:** `android-app/gradle.properties`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/gradlew`

**Файл:** `gradlew`
**Путь:** `android-app/gradlew`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/gradlew.bat`

**Файл:** `gradlew.bat`
**Путь:** `android-app/gradlew.bat`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Требует Windows cmd/PowerShell и установленный Python, если внутри вызывается python.

**Как проверить:**
- Запуск на Windows: `android-app/gradlew.bat`

### `android-app/local.properties`

**Файл:** `local.properties`
**Путь:** `android-app/local.properties`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/release-apk/PCControlMobile-v1.0.2.apk.idsig`

**Файл:** `PCControlMobile-v1.0.2.apk.idsig`
**Путь:** `android-app/release-apk/PCControlMobile-v1.0.2.apk.idsig`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `android-app/settings.gradle.kts`

**Файл:** `settings.gradle.kts`
**Путь:** `android-app/settings.gradle.kts`

**Назначение:** Android-клиент: Kotlin/Compose, Retrofit API, настройки URL, экраны мониторинга.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Привязан к настраиваемому серверному API, без жёсткого старого IP в коде.

**Какую проблему решает:**
- Решает необходимость подключать телефон к Linux-серверу через LAN/Tailscale URL.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `backend/app/api/__init__.py`

**Файл:** `__init__.py`
**Путь:** `backend/app/api/__init__.py`

**Назначение:** FastAPI роутер: HTTP endpoint-ы для сервера, агентов, телефона, файлов, медиа или задач.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- `python3 -m py_compile backend/app/api/__init__.py`

### `backend/app/api/agent_routes.py`

**Файл:** `agent_routes.py`
**Путь:** `backend/app/api/agent_routes.py`

**Назначение:** FastAPI роутер: HTTP endpoint-ы для сервера, агентов, телефона, файлов, медиа или задач.

**Техническая роль:**
- HTTP/WebSocket маршруты: `@router.post("/register")`, `@router.post("/heartbeat")`, `@router.get("/tasks/next")`, `@router.post("/tasks/{task_id}/result")`.
- Ключевые функции: `register`, `heartbeat`, `get_next_task`, `result`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `from datetime import datetime`, `from fastapi import APIRouter, Depends, Header, HTTPException, Request`, `from sqlalchemy.orm import Session`, `from ..auth import get_agent_from_token`, `from ..config import get_settings`, `from ..database import get_db`, `from ..models import Agent, Task`, `from ..schemas import AgentHeartbeatRequest, AgentRegisterRequest, TaskResultUpdate`.

**Как проверить:**
- `python3 -m py_compile backend/app/api/agent_routes.py`

### `backend/app/api/auth_routes.py`

**Файл:** `auth_routes.py`
**Путь:** `backend/app/api/auth_routes.py`

**Назначение:** FastAPI роутер: HTTP endpoint-ы для сервера, агентов, телефона, файлов, медиа или задач.

**Техническая роль:**
- HTTP/WebSocket маршруты: `@router.post("/login", response_model=TokenResponse)`.
- Ключевые функции: `login`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `from fastapi import APIRouter, HTTPException`, `from ..auth import create_access_token, verify_admin_token`, `from ..schemas import TokenRequest, TokenResponse`.

**Как проверить:**
- `python3 -m py_compile backend/app/api/auth_routes.py`

### `backend/app/api/camera.py`

**Файл:** `camera.py`
**Путь:** `backend/app/api/camera.py`

**Назначение:** FastAPI роутер: HTTP endpoint-ы для сервера, агентов, телефона, файлов, медиа или задач.

**Техническая роль:**
- HTTP/WebSocket маршруты: `@router.post("/api/agents/{agent_id}/camera/photo")`, `@router.post("/api/agents/{agent_id}/camera/record")`.
- Ключевые функции: `camera_photo`, `record_video`.

**Что было изменено:**
- Доработана серверная медиа-логика: фото вебки, видео, сохранение FileAsset.

**Какую проблему решает:**
- Решает ошибки камеры/видео, сохранение файлов в правильные storage-папки и browser-compatible видео.

**От чего зависит:**
- Python imports: `from fastapi import APIRouter, Depends, HTTPException`, `from sqlalchemy.orm import Session`, `from ..auth import get_current_admin`, `from ..config import get_settings`, `from ..database import get_db`, `from ..models import Agent`, `from ..services.task_service import create_task`.

**Как проверить:**
- `python3 -m py_compile backend/app/api/camera.py`

### `backend/app/api/files.py`

**Файл:** `files.py`
**Путь:** `backend/app/api/files.py`

**Назначение:** FastAPI роутер: HTTP endpoint-ы для сервера, агентов, телефона, файлов, медиа или задач.

**Техническая роль:**
- HTTP/WebSocket маршруты: `@router.post("/api/files/upload", response_model=FileAssetRead, dependencies=[Depends(_auth)])`, `@router.post("/api/agents/files/upload", response_model=FileAssetRead)`, `@router.get("/api/files", response_model=list[FileAssetRead], dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/files/categories", dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/files/photos", response_model=list[FileAssetRead], dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/files/screenshots", response_model=list[FileAssetRead], dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/files/videos", response_model=list[FileAssetRead], dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/files/telegram", response_model=list[FileAssetRead], dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/files/{file_id}", response_model=FileAssetRead, dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/files/{file_id}/download", dependencies=[Depends(get_access_key_admin)])`, `@router.delete("/api/files/{file_id}", dependencies=[Depends(get_current_admin)])`.
- Ключевые функции: `_auth`, `upload_file`, `upload_agent_file`, `list_files`, `categories`, `photos`, `screenshots`, `videos`, `telegram_files`, `file_details`, `download_file`, `delete_file`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `from fastapi import APIRouter, Depends, File, Query, UploadFile`, `from fastapi.responses import FileResponse`, `from sqlalchemy.orm import Session`, `from ..auth import get_access_key_admin, get_current_admin, get_agent_from_token`, `from ..database import get_db`, `from ..models import Agent, FileAsset`, `from ..schemas import FileAssetRead`, `from ..services.file_service import asset_path, create_asset_from_upload, get_asset_or_404`.

**Как проверить:**
- `python3 -m py_compile backend/app/api/files.py`

### `backend/app/api/mobile_routes.py`

**Файл:** `mobile_routes.py`
**Путь:** `backend/app/api/mobile_routes.py`

**Назначение:** FastAPI роутер: HTTP endpoint-ы для сервера, агентов, телефона, файлов, медиа или задач.

**Техническая роль:**
- HTTP/WebSocket маршруты: `@router.get("/config")`, `@router.get("/dashboard", response_model=DashboardResponse)`, `@router.get("/server-info")`, `@router.get("/connection-info")`, `@router.post("/server/screenshot")`, `@router.get("/server/screenshots")`, `@router.post("/server/webcam/photo")`, `@router.get("/server/webcam/photos")`, `@router.post("/server/webcam/record")`, `@router.get("/server/webcam/videos")`, `@router.get("/agents")`, `@router.get("/agents/{agent_id}")`, `@router.get("/agents/{agent_id}/processes")`, `@router.post("/agents/{agent_id}/processes/refresh")`, `@router.post("/agents/{agent_id}/screenshot")`, `@router.post("/agents/{agent_id}/camera/photo")`, `@router.post("/agents/{agent_id}/camera/record")`, `@router.get("/tasks")`, `@router.post("/tasks")`, `@router.post("/tasks/{task_id}/cancel")`, `@router.post("/tasks/{task_id}/retry")`, `@router.get("/logs")`, `@router.get("/files")`, `@router.post("/files/upload")`, `@router.get("/files/{file_id}/download")`, `@router.delete("/files/{file_id}")`, `@router.get("/photos")`, `@router.get("/screenshots")`, `@router.get("/videos")`, `@router.get("/screenshot/{agent_id}")`.
- Ключевые функции: `uptime_string`, `config`, `dashboard`, `mobile_server_info`, `mobile_connection_info`, `mobile_server_screenshot`, `mobile_server_screenshots`, `mobile_server_webcam_photo`, `mobile_server_webcam_photos`, `mobile_server_webcam_record`, `mobile_server_webcam_videos`, `agents`, `agent_details`, `mobile_agent_processes`, `mobile_refresh_processes`, `mobile_screenshot_task`, `mobile_camera_photo`, `mobile_camera_record`, `tasks`, `create_mobile_task`.

**Что было изменено:**
- Доработан/используется для Android-приложения и мобильных endpoint-ов.

**Какую проблему решает:**
- Решает несоответствие URL/API телефона и backend, ошибки 404 при мобильных действиях.

**От чего зависит:**
- Python imports: `import base64`, `import json`, `from datetime import datetime`, `from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile`, `from fastapi.responses import FileResponse, Response`, `from sqlalchemy.orm import Session`, `from ..auth import get_current_admin`, `from ..config import get_settings`.

**Как проверить:**
- `python3 -m py_compile backend/app/api/mobile_routes.py`

### `backend/app/api/processes.py`

**Файл:** `processes.py`
**Путь:** `backend/app/api/processes.py`

**Назначение:** FastAPI роутер: HTTP endpoint-ы для сервера, агентов, телефона, файлов, медиа или задач.

**Техническая роль:**
- HTTP/WebSocket маршруты: `@router.get("/api/agents/{agent_id}/processes")`, `@router.post("/api/agents/{agent_id}/processes/refresh")`.
- Ключевые функции: `get_processes`, `refresh_processes`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `import json`, `from fastapi import APIRouter, Depends, HTTPException`, `from sqlalchemy.orm import Session`, `from ..auth import get_current_admin`, `from ..database import get_db`, `from ..models import Agent, Task`, `from ..services.task_service import create_task`.

**Как проверить:**
- `python3 -m py_compile backend/app/api/processes.py`

### `backend/app/api/screenshots.py`

**Файл:** `screenshots.py`
**Путь:** `backend/app/api/screenshots.py`

**Назначение:** FastAPI роутер: HTTP endpoint-ы для сервера, агентов, телефона, файлов, медиа или задач.

**Техническая роль:**
- HTTP/WebSocket маршруты: `@router.post("/api/agents/{agent_id}/screenshot", dependencies=[Depends(get_current_admin)])`, `@router.get("/api/screenshots", dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/screenshots/{file_id}/download", dependencies=[Depends(get_access_key_admin)])`.
- Ключевые функции: `take_screenshot`, `screenshots`, `download_screenshot`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `from fastapi import APIRouter, Depends, HTTPException`, `from fastapi.responses import FileResponse`, `from sqlalchemy.orm import Session`, `from ..auth import get_access_key_admin, get_current_admin`, `from ..config import get_settings`, `from ..database import get_db`, `from ..models import Agent, FileAsset`, `from ..services.file_service import asset_path, get_asset_or_404`.

**Как проверить:**
- `python3 -m py_compile backend/app/api/screenshots.py`

### `backend/app/api/server.py`

**Файл:** `server.py`
**Путь:** `backend/app/api/server.py`

**Назначение:** FastAPI роутер: HTTP endpoint-ы для сервера, агентов, телефона, файлов, медиа или задач.

**Техническая роль:**
- HTTP/WebSocket маршруты: `@router.get("/api/server/info")`, `@router.get("/api/server/network")`, `@router.get("/api/agents/{agent_id}")`, `@router.get("/api/agents/{agent_id}/network")`.
- Ключевые функции: `info`, `network`, `agent_details`, `agent_network`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `from fastapi import APIRouter, Depends, Request`, `from sqlalchemy.orm import Session`, `from ..auth import get_access_key_admin`, `from ..database import get_db`, `from ..models import Agent`, `from ..services.agent_service import agent_to_mobile, compute_agent_status, list_agents`, `from ..services.network_service import server_info`, `from fastapi import HTTPException`.

**Как проверить:**
- `python3 -m py_compile backend/app/api/server.py`

### `backend/app/api/system_routes.py`

**Файл:** `system_routes.py`
**Путь:** `backend/app/api/system_routes.py`

**Назначение:** FastAPI роутер: HTTP endpoint-ы для сервера, агентов, телефона, файлов, медиа или задач.

**Техническая роль:**
- HTTP/WebSocket маршруты: `@router.get("/api/health", response_model=HealthResponse)`, `@router.get("/api/ping")`, `@router.get("/api/status", dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/system/status", dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/system/metrics", dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/logs", dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/system/logs", dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/agents", dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/tasks", dependencies=[Depends(get_access_key_admin)])`, `@router.post("/api/tasks/{task_id}/cancel", dependencies=[Depends(get_admin_or_access_key)])`, `@router.post("/api/tasks/{task_id}/retry", dependencies=[Depends(get_admin_or_access_key)])`, `@router.get("/api/server/features", dependencies=[Depends(get_admin_or_access_key)])`, `@router.get("/api/diagnostics", dependencies=[Depends(get_admin_or_access_key)])`, `@router.get("/api/wol/devices", dependencies=[Depends(get_admin_or_access_key)])`, `@router.post("/api/wol/wake/{device_name}", dependencies=[Depends(get_admin_or_access_key)])`, `@router.get("/api/media", dependencies=[Depends(get_admin_or_access_key)])`, `@router.post("/api/system/optimize/quick", dependencies=[Depends(get_access_key_admin)])`, `@router.post("/api/system/optimize/deep", dependencies=[Depends(get_access_key_admin)])`, `@router.post("/api/system/optimize/temp", dependencies=[Depends(get_access_key_admin)])`, `@router.post("/api/system/restart-agent", dependencies=[Depends(get_access_key_admin)])`, `@router.post("/api/system/restart-pc", dependencies=[Depends(get_access_key_admin)])`, `@router.post("/api/system/shutdown-pc", dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/files", dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/files/{file_id}", dependencies=[Depends(get_access_key_admin)])`, `@router.get("/api/mobile/screenshot", dependencies=[Depends(get_access_key_admin)])`.
- Ключевые функции: `health`, `ping`, `status_payload`, `status`, `legacy_status`, `legacy_metrics`, `logs_payload`, `logs`, `legacy_logs`, `api_agents`, `api_tasks`, `api_cancel_task`, `api_retry_task`, `server_features`, `diagnostics`, `writable`, `wol_devices`, `wol_wake`, `api_media`, `_first_agent`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `import base64`, `import json`, `import shutil`, `import socket`, `import time`, `from datetime import datetime`, `from pathlib import Path`, `from fastapi import APIRouter, Depends, HTTPException`.

**Как проверить:**
- `python3 -m py_compile backend/app/api/system_routes.py`

### `backend/app/bot/__init__.py`

**Файл:** `__init__.py`
**Путь:** `backend/app/bot/__init__.py`

**Назначение:** Telegram-бот: команды, inline-кнопки, русская локализация, runner polling.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Переведён/доработан Telegram-бот, callback-кнопки и сообщения на русском.

**Какую проблему решает:**
- Решает неработающие inline-кнопки, английские сообщения и нестабильные ответы Telegram.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- `python3 -m py_compile backend/app/bot/__init__.py`

### `backend/app/bot/lang_ru.py`

**Файл:** `lang_ru.py`
**Путь:** `backend/app/bot/lang_ru.py`

**Назначение:** Telegram-бот: команды, inline-кнопки, русская локализация, runner polling.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Переведён/доработан Telegram-бот, callback-кнопки и сообщения на русском.

**Какую проблему решает:**
- Решает неработающие inline-кнопки, английские сообщения и нестабильные ответы Telegram.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- `python3 -m py_compile backend/app/bot/lang_ru.py`

### `backend/app/bot/runner.py`

**Файл:** `runner.py`
**Путь:** `backend/app/bot/runner.py`

**Назначение:** Telegram-бот: команды, inline-кнопки, русская локализация, runner polling.

**Техническая роль:**
- Ключевые функции: `main`.

**Что было изменено:**
- Переведён/доработан Telegram-бот, callback-кнопки и сообщения на русском.

**Какую проблему решает:**
- Решает неработающие inline-кнопки, английские сообщения и нестабильные ответы Telegram.

**От чего зависит:**
- Python imports: `from ..database import Base, engine, ensure_database_schema`, `from ..utils.logging import setup_logging`, `from .telegram_bot import run_bot_forever`.

**Как проверить:**
- `python3 -m py_compile backend/app/bot/runner.py`

### `backend/app/bot/telegram_bot.py`

**Файл:** `telegram_bot.py`
**Путь:** `backend/app/bot/telegram_bot.py`

**Назначение:** Telegram-бот: команды, inline-кнопки, русская локализация, runner polling.

**Техническая роль:**
- Ключевые функции: `is_owner`, `main_menu_keyboard`, `back_keyboard`, `files_keyboard`, `confirm_keyboard`, `send_safe`, `safe_bot_log`, `answer_callback`, `owner_only`, `callback_owner_only`, `start_text`, `status_text`, `server_ip_text`, `diagnostics_text`, `wol_text`, `wol_keyboard`, `agents_text`, `file_type_title`, `file_list_text`, `tasks_text`.

**Что было изменено:**
- Переведён/доработан Telegram-бот, callback-кнопки и сообщения на русском.

**Какую проблему решает:**
- Решает неработающие inline-кнопки, английские сообщения и нестабильные ответы Telegram.

**От чего зависит:**
- Python imports: `import json`, `import logging`, `import threading`, `import time`, `from datetime import datetime`, `import telebot`, `from telebot import types`, `from ..config import get_settings`.

**Как проверить:**
- `python3 -m py_compile backend/app/bot/telegram_bot.py`

### `backend/app/config.py`

**Файл:** `config.py`
**Путь:** `backend/app/config.py`

**Назначение:** Централизованные настройки из env: порты, пути, токены, флаги функций, лимиты.

**Техническая роль:**
- Классы: `Settings`.
- Ключевые функции: `allowed_scripts`, `allowed_upload_exts`, `allowed_telegram_ids`, `wol_device_map`, `apply_json_config`, `get_settings`.

**Что было изменено:**
- Секреты и флаги вынесены в конфигурацию, реальные значения не должны храниться в коде.

**Какую проблему решает:**
- Решает риск хардкода токенов, IP, access key и feature flags.

**От чего зависит:**
- Python imports: `import json`, `import os`, `from functools import lru_cache`, `from pathlib import Path`, `from pydantic import AliasChoices, Field`, `from pydantic_settings import BaseSettings, SettingsConfigDict`.

**Как проверить:**
- `python3 -m py_compile backend/app/config.py`

### `backend/app/main.py`

**Файл:** `main.py`
**Путь:** `backend/app/main.py`

**Назначение:** Точка входа FastAPI: создаёт приложение, подключает API, WebSocket и веб-панель.

**Техническая роль:**
- HTTP/WebSocket маршруты: `@app.get("/")`, `@app.get("/panel", response_class=HTMLResponse)`, `@app.websocket("/ws/status")`, `@app.websocket("/ws/agent")`.
- Ключевые функции: `rate_limit_middleware`, `startup_event`, `root`, `panel`, `status_ws`, `agent_ws`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `from datetime import datetime`, `import ipaddress`, `from pathlib import Path`, `import time`, `from collections import defaultdict, deque`, `from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect`, `from fastapi.middleware.cors import CORSMiddleware`, `from fastapi.responses import HTMLResponse`.

**Как проверить:**
- `python3 -m py_compile backend/app/main.py`

### `backend/app/services/agent_service.py`

**Файл:** `agent_service.py`
**Путь:** `backend/app/services/agent_service.py`

**Назначение:** Сервисный слой: бизнес-логика задач, файлов, агентов, медиа, сети или диагностики.

**Техническая роль:**
- Ключевые функции: `compute_agent_status`, `ensure_agent`, `update_heartbeat`, `list_agents`, `agent_to_mobile`, `screenshot_allowed`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `import secrets`, `from datetime import datetime, timedelta`, `from sqlalchemy.orm import Session`, `from ..config import get_settings`, `from ..models import Agent`.

**Как проверить:**
- `python3 -m py_compile backend/app/services/agent_service.py`

### `backend/app/services/file_service.py`

**Файл:** `file_service.py`
**Путь:** `backend/app/services/file_service.py`

**Назначение:** Сервисный слой: бизнес-логика задач, файлов, агентов, медиа, сети или диагностики.

**Техническая роль:**
- Ключевые функции: `validate_upload_name`, `create_asset_from_bytes`, `create_asset_from_upload`, `get_asset_or_404`, `asset_path`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `import mimetypes`, `from pathlib import Path`, `from fastapi import HTTPException, UploadFile`, `from sqlalchemy.orm import Session`, `from ..config import get_settings`, `from ..models import FileAsset`, `from ..utils.hashing import sha256_file`, `from ..utils.paths import public_type_dir, safe_filename`.

**Как проверить:**
- `python3 -m py_compile backend/app/services/file_service.py`

### `backend/app/services/log_service.py`

**Файл:** `log_service.py`
**Путь:** `backend/app/services/log_service.py`

**Назначение:** Сервисный слой: бизнес-логика задач, файлов, агентов, медиа, сети или диагностики.

**Техническая роль:**
- Ключевые функции: `add_log`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `from datetime import datetime`, `from sqlalchemy.orm import Session`, `from ..models import LogEntry`, `from ..utils.logging import append_json_log`.

**Как проверить:**
- `python3 -m py_compile backend/app/services/log_service.py`

### `backend/app/services/network_service.py`

**Файл:** `network_service.py`
**Путь:** `backend/app/services/network_service.py`

**Назначение:** Сервисный слой: бизнес-логика задач, файлов, агентов, медиа, сети или диагностики.

**Техническая роль:**
- Ключевые функции: `get_local_ip`, `server_info`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `import socket`, `import time`, `from ..config import get_settings`.

**Как проверить:**
- `python3 -m py_compile backend/app/services/network_service.py`

### `backend/app/services/server_media_service.py`

**Файл:** `server_media_service.py`
**Путь:** `backend/app/services/server_media_service.py`

**Назначение:** Сервисный слой: бизнес-логика задач, файлов, агентов, медиа, сети или диагностики.

**Техническая роль:**
- Ключевые функции: `_write_error`, `create_server_screenshot`, `create_server_webcam_photo`, `create_server_webcam_video`.

**Что было изменено:**
- Доработана серверная медиа-логика: фото вебки, видео, сохранение FileAsset.

**Какую проблему решает:**
- Решает ошибки камеры/видео, сохранение файлов в правильные storage-папки и browser-compatible видео.

**От чего зависит:**
- Python imports: `import logging`, `import tempfile`, `import time`, `from pathlib import Path`, `from fastapi import HTTPException`, `from sqlalchemy.orm import Session`, `from ..config import get_settings`, `from .file_service import create_asset_from_bytes`.

**Как проверить:**
- `python3 -m py_compile backend/app/services/server_media_service.py`

### `backend/app/services/task_service.py`

**Файл:** `task_service.py`
**Путь:** `backend/app/services/task_service.py`

**Назначение:** Сервисный слой: бизнес-логика задач, файлов, агентов, медиа, сети или диагностики.

**Техническая роль:**
- Ключевые функции: `is_safe_retry_action`, `create_task`, `expire_running_tasks`, `next_task`, `finish_task`, `cancel_task`, `retry_task`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `import uuid`, `from datetime import datetime, timedelta`, `from sqlalchemy.orm import Session`, `from ..config import get_settings`, `from ..models import Agent, Task`, `from .agent_service import DANGEROUS_ACTIONS, SAFE_ACTIONS`.

**Как проверить:**
- `python3 -m py_compile backend/app/services/task_service.py`

### `backend/app/services/wol_service.py`

**Файл:** `wol_service.py`
**Путь:** `backend/app/services/wol_service.py`

**Назначение:** Сервисный слой: бизнес-логика задач, файлов, агентов, медиа, сети или диагностики.

**Техническая роль:**
- Классы: `WolDevice`.
- Ключевые функции: `normalize_mac`, `list_wol_devices`, `build_magic_packet`, `wake_device`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `import re`, `import socket`, `from dataclasses import dataclass`, `from ..config import get_settings`.

**Как проверить:**
- `python3 -m py_compile backend/app/services/wol_service.py`

### `backend/app/utils/hashing.py`

**Файл:** `hashing.py`
**Путь:** `backend/app/utils/hashing.py`

**Назначение:** Утилиты: пути, безопасность, hashing, audit helpers.

**Техническая роль:**
- Ключевые функции: `sha256_file`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `import hashlib`, `from pathlib import Path`.

**Как проверить:**
- `python3 -m py_compile backend/app/utils/hashing.py`

### `backend/app/utils/logging.py`

**Файл:** `logging.py`
**Путь:** `backend/app/utils/logging.py`

**Назначение:** Утилиты: пути, безопасность, hashing, audit helpers.

**Техническая роль:**
- Ключевые функции: `setup_logging`, `append_json_log`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `import json`, `import logging`, `from logging.handlers import RotatingFileHandler`, `from pathlib import Path`, `from ..config import get_settings`.

**Как проверить:**
- `python3 -m py_compile backend/app/utils/logging.py`

### `backend/app/utils/paths.py`

**Файл:** `paths.py`
**Путь:** `backend/app/utils/paths.py`

**Назначение:** Утилиты: пути, безопасность, hashing, audit helpers.

**Техническая роль:**
- Ключевые функции: `storage_root`, `public_type_dir`, `safe_filename`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `import re`, `import uuid`, `from pathlib import Path`, `from ..config import get_settings`.

**Как проверить:**
- `python3 -m py_compile backend/app/utils/paths.py`

### `backend/app/web/panel.html`

**Файл:** `panel.html`
**Путь:** `backend/app/web/panel.html`

**Назначение:** Веб-панель, которую FastAPI отдаёт по HTTP.

**Техническая роль:**
- Используемые API: `/api/auth/login`, `/api/diagnostics`, `/api/media`, `/api/mobile/agents`, `/api/mobile/dashboard`, `/api/mobile/files`, `/api/mobile/files/upload?public_type=upload`, `/api/mobile/logs`, `/api/mobile/server-info`, `/api/mobile/server/screenshot`, `/api/mobile/server/webcam/photo?confirmed=true`, `/api/mobile/server/webcam/record?duration_seconds=10&confirmed=true`, `/api/mobile/tasks`, `/api/ping`, `/api/server/features`, `/api/wol/devices`.

**Что было изменено:**
- Доработана веб-панель: тёмный UI, страницы сервера/агентов/файлов/медиа, мобильные API.

**Какую проблему решает:**
- Решает пустой Dashboard, неправильные endpoint-ы и ошибки Not Found на кнопках сайта.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Открыть сайт: `http://192.168.0.194:8765/` или `http://100.91.196.119:8765/`.

### `backend/app/websocket/manager.py`

**Файл:** `manager.py`
**Путь:** `backend/app/websocket/manager.py`

**Назначение:** WebSocket менеджер и live-события для телефона/панели/агентов.

**Техническая роль:**
- Классы: `WebSocketManager`.
- Ключевые функции: `__init__`, `connect`, `disconnect`, `broadcast`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Python imports: `from collections import defaultdict`, `from typing import Any`, `from fastapi import WebSocket`.

**Как проверить:**
- `python3 -m py_compile backend/app/websocket/manager.py`

### `config.example.json`

**Файл:** `config.example.json`
**Путь:** `config.example.json`

**Назначение:** Пример JSON-конфига без реальных секретов.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Секреты и флаги вынесены в конфигурацию, реальные значения не должны храниться в коде.

**Какую проблему решает:**
- Решает риск хардкода токенов, IP, access key и feature flags.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `install_ubuntu.sh`

**Файл:** `install_ubuntu.sh`
**Путь:** `install_ubuntu.sh`

**Назначение:** Установщик Ubuntu: системные пакеты, пользователь, каталоги, venv, зависимости и systemd.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Требует Linux shell, systemctl/journalctl или стандартные утилиты, если они вызываются внутри файла.

**Как проверить:**
- `bash -n install_ubuntu.sh`

### `install_windows.bat`

**Файл:** `install_windows.bat`
**Путь:** `install_windows.bat`

**Назначение:** Windows-скрипт для старого/локального запуска проекта.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Требует Windows cmd/PowerShell и установленный Python, если внутри вызывается python.

**Как проверить:**
- Запуск на Windows: `install_windows.bat`

### `MIGRATION_WINDOWS_TO_UBUNTU.md`

**Файл:** `MIGRATION_WINDOWS_TO_UBUNTU.md`
**Путь:** `MIGRATION_WINDOWS_TO_UBUNTU.md`

**Назначение:** Документ миграции с Windows-запуска на Ubuntu Server 24.04 LTS.

**Техническая роль:**
- Разделы документа: `Миграция сервера с Windows на Ubuntu Server 24.04 LTS`, `Что было на Windows`, `Что стало на Ubuntu`, `Главные изменённые файлы`, `Как перенести config`, `Как перенести базу и логи`, `Как запустить`, `Как проверить`, `Как подключить Windows-агента к Linux-серверу`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Открыть файл и сверить команды из разделов проверки.

### `pc-agent/agent.py`

**Файл:** `agent.py`
**Путь:** `pc-agent/agent.py`

**Назначение:** Windows PC-агент: подключение к серверу, выполнение allowlist-задач, статус и медиа.

**Техническая роль:**
- Ключевые функции: `load_config`, `env`, `load_state`, `save_state`, `local_ip`, `auth_headers`, `post`, `upload_file`, `get`, `register_if_needed`, `websocket_send_event`, `system_info`, `disk_info`, `network_info`, `process_list`, `heartbeat_payload`, `make_screenshot_file`, `make_screenshot_result`, `recording_indicator`, `poll`.

**Что было изменено:**
- Оставлен как Windows-агент, который подключается к Linux-серверу по HTTP/WebSocket.

**Какую проблему решает:**
- Решает разделение серверной Linux-части и Windows-логики агента.

**От чего зависит:**
- Python imports: `import base64`, `import hashlib`, `import json`, `import logging`, `import os`, `import platform`, `import random`, `import shutil`.

**Как проверить:**
- `python3 -m py_compile pc-agent/agent.py`

### `pc-agent/agent_config.example.json`

**Файл:** `agent_config.example.json`
**Путь:** `pc-agent/agent_config.example.json`

**Назначение:** Windows PC-агент: подключение к серверу, выполнение allowlist-задач, статус и медиа.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Оставлен как Windows-агент, который подключается к Linux-серверу по HTTP/WebSocket.

**Какую проблему решает:**
- Решает разделение серверной Linux-части и Windows-логики агента.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `pc-agent/logs/agent.log`

**Файл:** `agent.log`
**Путь:** `pc-agent/logs/agent.log`

**Назначение:** Windows PC-агент: подключение к серверу, выполнение allowlist-задач, статус и медиа.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Оставлен как Windows-агент, который подключается к Linux-серверу по HTTP/WebSocket.

**Какую проблему решает:**
- Решает разделение серверной Linux-части и Windows-логики агента.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Проверяется через общий запуск проекта и просмотр соответствующей функции в UI/API.

### `pc-agent/requirements.txt`

**Файл:** `requirements.txt`
**Путь:** `pc-agent/requirements.txt`

**Назначение:** Windows PC-агент: подключение к серверу, выполнение allowlist-задач, статус и медиа.

**Техническая роль:**
- Зависимости: `requests>=2.32.5`, `psutil>=7.1.0`, `pillow>=12.0.0`, `websockets>=15.0.0`, `opencv-python>=4.10.0`.

**Что было изменено:**
- Оставлен как Windows-агент, который подключается к Linux-серверу по HTTP/WebSocket.

**Какую проблему решает:**
- Решает разделение серверной Linux-части и Windows-логики агента.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- `/opt/pcmanager/venv/bin/python -m pip install -r requirements.txt`

### `README.md`

**Файл:** `README.md`
**Путь:** `README.md`

**Назначение:** Главная инструкция по установке, запуску, подключению сервера, Telegram-бота, агента и телефона.

**Техническая роль:**
- Разделы документа: `PC Control Personal Server`, `Структура`, `Установка на Ubuntu Server 24.04 LTS`, `Настройка .env`, `Запуск и автозапуск`, `Доступ не только дома`, `Wake-on-LAN`, `Проверка API`, `Telegram-бот`, `Подключение Windows-агента`, `Файлы, скриншоты, процессы, камера`, `Скрин экрана и вебка сервера`, `Подключение телефона`, `Reverse proxy`, `Troubleshooting`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- Открыть файл и сверить команды из разделов проверки.

### `requirements.txt`

**Файл:** `requirements.txt`
**Путь:** `requirements.txt`

**Назначение:** Список Python-зависимостей backend, Telegram-бота, API, WebSocket и сервисных модулей.

**Техническая роль:**
- Зависимости: `fastapi>=0.121.0`, `uvicorn[standard]>=0.38.0`, `sqlalchemy>=2.0.44`, `pydantic>=2.12.0`, `pydantic-settings>=2.11.0`, `python-jose[cryptography]>=3.5.0`, `passlib[bcrypt]>=1.7.4`, `python-dotenv>=1.2.0`, `pyTelegramBotAPI>=4.29.0`, `requests>=2.32.5`, `psutil>=7.1.0`, `pillow>=12.0.0`, `websockets>=15.0.0`, `httpx>=0.28.0`, `python-multipart>=0.0.20`.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Зависит от общей структуры проекта и настроек, указанных в README/.env.example.

**Как проверить:**
- `/opt/pcmanager/venv/bin/python -m pip install -r requirements.txt`

### `run_agent.bat`

**Файл:** `run_agent.bat`
**Путь:** `run_agent.bat`

**Назначение:** Windows-скрипт запуска агента.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Требует Windows cmd/PowerShell и установленный Python, если внутри вызывается python.

**Как проверить:**
- Запуск на Windows: `run_agent.bat`

### `run_server.bat`

**Файл:** `run_server.bat`
**Путь:** `run_server.bat`

**Назначение:** Windows-скрипт запуска backend.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Явных изменений по истории git не определить; файл входит в текущую рабочую структуру проекта.

**Какую проблему решает:**
- Поддерживает целостность проекта или документацию, прямой баг фиксирует не всегда.

**От чего зависит:**
- Требует Windows cmd/PowerShell и установленный Python, если внутри вызывается python.

**Как проверить:**
- Запуск на Windows: `run_server.bat`

### `scripts/backup.sh`

**Файл:** `backup.sh`
**Путь:** `scripts/backup.sh`

**Назначение:** Linux-скрипт управления, диагностики, backup/update или ежедневной проверки.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Требует Linux shell, systemctl/journalctl или стандартные утилиты, если они вызываются внутри файла.

**Как проверить:**
- `bash -n scripts/backup.sh`

### `scripts/install_server_daily_self_check.sh`

**Файл:** `install_server_daily_self_check.sh`
**Путь:** `scripts/install_server_daily_self_check.sh`

**Назначение:** Linux-скрипт управления, диагностики, backup/update или ежедневной проверки.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Требует Linux shell, systemctl/journalctl или стандартные утилиты, если они вызываются внутри файла.

**Как проверить:**
- `bash -n scripts/install_server_daily_self_check.sh`

### `scripts/logs.sh`

**Файл:** `logs.sh`
**Путь:** `scripts/logs.sh`

**Назначение:** Linux-скрипт управления, диагностики, backup/update или ежедневной проверки.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Требует Linux shell, systemctl/journalctl или стандартные утилиты, если они вызываются внутри файла.

**Как проверить:**
- `bash -n scripts/logs.sh`

### `scripts/restart.sh`

**Файл:** `restart.sh`
**Путь:** `scripts/restart.sh`

**Назначение:** Linux-скрипт управления, диагностики, backup/update или ежедневной проверки.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Требует Linux shell, systemctl/journalctl или стандартные утилиты, если они вызываются внутри файла.

**Как проверить:**
- `bash -n scripts/restart.sh`

### `scripts/server_daily_self_check.sh`

**Файл:** `server_daily_self_check.sh`
**Путь:** `scripts/server_daily_self_check.sh`

**Назначение:** Linux-скрипт управления, диагностики, backup/update или ежедневной проверки.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Требует Linux shell, systemctl/journalctl или стандартные утилиты, если они вызываются внутри файла.

**Как проверить:**
- `bash -n scripts/server_daily_self_check.sh`

### `scripts/start.sh`

**Файл:** `start.sh`
**Путь:** `scripts/start.sh`

**Назначение:** Linux-скрипт управления, диагностики, backup/update или ежедневной проверки.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Требует Linux shell, systemctl/journalctl или стандартные утилиты, если они вызываются внутри файла.

**Как проверить:**
- `bash -n scripts/start.sh`

### `scripts/status.sh`

**Файл:** `status.sh`
**Путь:** `scripts/status.sh`

**Назначение:** Linux-скрипт управления, диагностики, backup/update или ежедневной проверки.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Требует Linux shell, systemctl/journalctl или стандартные утилиты, если они вызываются внутри файла.

**Как проверить:**
- `bash -n scripts/status.sh`

### `scripts/stop.sh`

**Файл:** `stop.sh`
**Путь:** `scripts/stop.sh`

**Назначение:** Linux-скрипт управления, диагностики, backup/update или ежедневной проверки.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Требует Linux shell, systemctl/journalctl или стандартные утилиты, если они вызываются внутри файла.

**Как проверить:**
- `bash -n scripts/stop.sh`

### `scripts/update.sh`

**Файл:** `update.sh`
**Путь:** `scripts/update.sh`

**Назначение:** Linux-скрипт управления, диагностики, backup/update или ежедневной проверки.

**Техническая роль:**
- Работает как часть общей структуры проекта; конкретная роль определяется папкой и подключением из соседних модулей.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Требует Linux shell, systemctl/journalctl или стандартные утилиты, если они вызываются внутри файла.

**Как проверить:**
- `bash -n scripts/update.sh`

### `systemd/pcmanager-bot.service`

**Файл:** `pcmanager-bot.service`
**Путь:** `systemd/pcmanager-bot.service`

**Назначение:** Шаблон systemd service для автозапуска на Ubuntu.

**Техническая роль:**
- Рабочая директория: `WorkingDirectory=/opt/pcmanager`.
- Команда запуска: `ExecStart=/opt/pcmanager/venv/bin/python -m backend.app.bot.runner`.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Используется systemd, пользователь pcmanager, venv и `/etc/pcmanager/pcmanager.env`.

**Как проверить:**
- `sudo systemd-analyze verify systemd/pcmanager-bot.service`

### `systemd/pcmanager-server.service`

**Файл:** `pcmanager-server.service`
**Путь:** `systemd/pcmanager-server.service`

**Назначение:** Шаблон systemd service для автозапуска на Ubuntu.

**Техническая роль:**
- Рабочая директория: `WorkingDirectory=/opt/pcmanager`.
- Команда запуска: `ExecStart=/opt/pcmanager/venv/bin/python -m uvicorn backend.app.main:app --host ${SERVER_HOST} --port ${SERVER_PORT}`.

**Что было изменено:**
- Добавлен/адаптирован для Ubuntu Server, systemd и 24/7 эксплуатации.

**Какую проблему решает:**
- Решает ручной Windows-запуск, отсутствие автозапуска, логов и стандартного управления сервисами.

**От чего зависит:**
- Используется systemd, пользователь pcmanager, venv и `/etc/pcmanager/pcmanager.env`.

**Как проверить:**
- `sudo systemd-analyze verify systemd/pcmanager-server.service`

## 5. Что сделано для Linux/Ubuntu

- Windows-only запуск через `.bat`, `.exe` и ручной старт из консоли вынесен из серверной части: сервер запускается как Python/FastAPI приложение на Ubuntu.
- Серверные пути нормализованы под Linux: `/opt/pcmanager` для установленного кода, `/etc/pcmanager` для конфигурации, `/var/log/pcmanager` для логов, `/var/lib/pcmanager` для базы и storage.
- Реальные секреты должны храниться в `/etc/pcmanager/pcmanager.env`, а не в коде и не в репозитории.
- Python venv используется как `/opt/pcmanager/venv`; systemd запускает именно этот интерпретатор.
- Windows-агент оставлен отдельной частью: он подключается к Linux-серверу по HTTP/WebSocket и выполняет только разрешённые задачи.
- FastAPI работает на Ubuntu Server 24.04 через uvicorn и отдаёт API, WebSocket и веб-панель с одного порта `8765`.

## 6. Что сделано для systemd

- `pcmanager-server.service` запускает FastAPI/uvicorn.
- `pcmanager-bot.service` запускает Telegram polling runner.
- `enabled` означает, что сервис стартует автоматически после загрузки Ubuntu.
- `active (running)` означает, что процесс сейчас жив и systemd считает его рабочим.
- `inactive (dead)` у бота возможно, если Telegram-токен не задан, сеть/DNS Telegram недоступны или runner завершился без перезапуска.
- Логи смотрятся через `journalctl`, а файловые логи — в `/var/log/pcmanager`.

```bash
sudo systemctl status pcmanager-server
sudo systemctl status pcmanager-bot
sudo systemctl restart pcmanager-server
sudo systemctl restart pcmanager-bot
sudo journalctl -u pcmanager-server -f
sudo journalctl -u pcmanager-bot -f
```

## 7. Что было исправлено

### Windows-only запуск
**Проблема:** Сервер был завязан на Windows `.bat/.exe` и ручной запуск.
**Исправление:** Добавлены Linux install/systemd/scripts и перенос путей на `/opt`, `/etc`, `/var/log`, `/var/lib`.
**Файлы:**
- `install_ubuntu.sh`
- `systemd/pcmanager-server.service`
- `systemd/pcmanager-bot.service`
- `scripts/*.sh`
**Результат:** Сервер запускается на Ubuntu через systemd.

### Отсутствие автозапуска
**Проблема:** После перезагрузки сервер и бот нужно было поднимать вручную.
**Исправление:** Добавлены systemd service-файлы с автоперезапуском.
**Файлы:**
- `systemd/pcmanager-server.service`
- `systemd/pcmanager-bot.service`
**Результат:** Сервисы можно включать и проверять через systemctl.

### Нормальные логи
**Проблема:** Ошибки было трудно искать по разным консолям.
**Исправление:** Логи вынесены в journalctl и `/var/log/pcmanager`, добавлены диагностические скрипты.
**Файлы:**
- `scripts/logs.sh`
- `scripts/status.sh`
- `scripts/server_daily_self_check.sh`
**Результат:** Состояние можно проверять одной командой и ежедневным отчётом.

### Telegram bot disabled/not configured
**Проблема:** Бот мог не стартовать или падать из-за Telegram/DNS/токена.
**Исправление:** Токен вынесен в env, runner работает отдельным сервисом, добавлены русские тексты и callback handlers.
**Файлы:**
- `backend/app/bot/runner.py`
- `backend/app/bot/telegram_bot.py`
- `backend/app/bot/lang_ru.py`
**Результат:** Бот запускается отдельно и кнопки отвечают через callback_query.

### Миграция на Linux
**Проблема:** Серверная часть смешивалась с Windows-логикой агента.
**Исправление:** Проект разделён на backend, pc-agent, android-app и systemd/scripts.
**Файлы:**
- `backend/`
- `pc-agent/`
- `android-app/`
- `systemd/`
**Результат:** Linux-сервер не требует Windows API, а Windows-функции остаются в агенте.

### Подключение Windows-агента к Linux
**Проблема:** Агент должен видеть новый сервер и не считаться самим сервером.
**Исправление:** API/WS и конфиг агента отделены от server runtime.
**Файлы:**
- `pc-agent/`
- `backend/app/api/agents.py`
- `backend/app/websocket/manager.py`
**Результат:** Агент подключается к `http://SERVER:8765` и виден в списке агентов.

### API ping/health
**Проблема:** Не было простой проверки, что backend жив.
**Исправление:** Добавлены `/api/ping` и `/api/health`.
**Файлы:**
- `backend/app/main.py`
- `backend/app/api/server.py`
**Результат:** `curl http://127.0.0.1:8765/api/ping` возвращает ответ.

### WebSocket/live status
**Проблема:** Телефону/панели нужен live-статус без спама Telegram.
**Исправление:** Добавлен WebSocket manager и `/ws/status`.
**Файлы:**
- `backend/app/websocket/manager.py`
- `backend/app/main.py`
**Результат:** Клиенты могут получать live-события через WebSocket.

### Мобильные URL
**Проблема:** Android-приложение ловило 404/старые IP.
**Исправление:** Endpoint-ы телефона централизованы и добавлены mobile routes.
**Файлы:**
- `backend/app/api/mobile_routes.py`
- `android-app/`
**Результат:** Телефон использует настраиваемые Base URL/WebSocket URL.

### Безопасность токенов
**Проблема:** .env и токены нельзя держать в коде.
**Исправление:** Настройки вынесены в `.env.example`/`/etc/pcmanager/pcmanager.env`, отчёты маскируют секреты.
**Файлы:**
- `backend/app/config.py`
- `.env.example`
**Результат:** Секреты можно менять без изменения кода.

### Backup/update/diagnostics
**Проблема:** Не было безопасного ежедневного контроля.
**Исправление:** Добавлены backup/update/status/logs и self-check scripts.
**Файлы:**
- `scripts/backup.sh`
- `scripts/update.sh`
- `scripts/server_daily_self_check.sh`
**Результат:** Можно проверять сервисы и получать отчёты без ручного перебора логов.

### Сайт и медиа
**Проблема:** Веб-панель показывала пустой Dashboard/404 на вебке и видео.
**Исправление:** Доработаны mobile routes, panel.html, storage paths и server media service.
**Файлы:**
- `backend/app/web/panel.html`
- `backend/app/api/mobile_routes.py`
- `backend/app/services/server_media_service.py`
- `backend/app/utils/paths.py`
**Результат:** Сайт открывается по IP, кнопки фото/видео вызывают backend, файлы сохраняются в storage.

## 8. Карта проекта

| Компонент | Папка/файлы | За что отвечает | Как проверить |
|---|---|---|---|
| FastAPI backend | `backend/app/main.py`, `backend/app/api/*`, `backend/app/services/*` | HTTP API, web panel, health, tasks, files, media | `curl http://127.0.0.1:8765/api/ping` |
| Telegram bot | `backend/app/bot/*` | Команды Telegram, inline-кнопки, уведомления владельцу | `sudo systemctl status pcmanager-bot` и `/start` в Telegram |
| WebSocket server | `backend/app/websocket/*`, `backend/app/main.py` | Live-статус и события для телефона/панели/агентов | Подключение к `ws://SERVER:8765/ws/status` |
| Windows agent | `pc-agent/*` | Сбор статуса ПК, выполнение allowlist-задач, скриншоты/процессы | Запустить агент и проверить `/api/agents` |
| Android app | `android-app/*` | Мобильный клиент, настройки URL, API/WS, экраны управления | `cd android-app && ./gradlew assembleDebug` |
| Systemd services | `systemd/*.service` | Автозапуск backend и Telegram-бота | `sudo systemctl status pcmanager-server pcmanager-bot` |
| Install scripts | `install_ubuntu.sh`, `install_windows.bat` | Установка окружения на Ubuntu/Windows | `bash -n install_ubuntu.sh` |
| Config/env | `.env.example`, `config.example.json`, `backend/app/config.py` | Настройки, feature flags, секреты через env | Проверить `/etc/pcmanager/pcmanager.env` без вывода секретов |
| Logs | `/var/log/pcmanager`, `scripts/logs.sh` | Журнал ошибок, bot/server logs | `sudo journalctl -u pcmanager-server -n 100 --no-pager` |
| Backup/update scripts | `scripts/backup.sh`, `scripts/update.sh` | Резервное копирование и обновление проекта | `bash -n scripts/backup.sh` |
| Diagnostics/tools | `scripts/server_daily_self_check.sh`, `tools/*` если есть | Проверки API, сервисов, диска, RAM и логов | `bash scripts/server_daily_self_check.sh` |

## 9. Команды проверки

```bash
# Проверить API локально
curl http://127.0.0.1:8765/api/ping

# Проверить LAN API
curl http://192.168.0.194:8765/api/ping

# Проверить порт
ss -tulpn | grep 8765

# Проверить сервисы
sudo systemctl status pcmanager-server
sudo systemctl status pcmanager-bot

# Проверить логи
sudo journalctl -u pcmanager-server -n 100 --no-pager
sudo journalctl -u pcmanager-bot -n 100 --no-pager

# Проверить Python-файлы проекта
cd /home/pc/PCControlPersonal_Project
python3 -m compileall backend

# Проверить installed/live services
curl http://127.0.0.1:8765/api/health
sudo systemctl restart pcmanager-server pcmanager-bot
sudo systemctl status pcmanager-server pcmanager-bot --no-pager -l
```

## 10. Что уже работает, что частично, что требует настройки

### Уже работает
- FastAPI backend запускается на Ubuntu через systemd.
- `/api/ping` и `/api/health` используются для проверки живости сервера.
- Telegram-бот вынесен в отдельный сервис.
- Веб-панель открывается по IP сервера и через Tailscale, если Tailscale включён.
- Storage-папки для файлов/медиа разделены по категориям.
- Windows-агент архитектурно отделён от Linux-сервера.

### Частично работает или зависит от железа/настроек
- Скриншот экрана сервера на Ubuntu без GUI будет возвращать понятную ошибку: активного графического экрана нет.
- Фото/видео вебки сервера работает только если есть камера, права доступа к `/dev/video*` и включены env-флаги.
- Wake-on-LAN зависит от сетевой карты, BIOS/UEFI, коммутатора и поддержки WOL на устройстве.
- Telegram зависит от DNS/доступа к `api.telegram.org`; при сбое сети кнопки могут не отвечать до восстановления связи.

### Требует настройки
- `/etc/pcmanager/pcmanager.env` должен содержать реальные значения токенов и owner id, но их нельзя коммитить или печатать в логах.
- Windows agent нужно направить на `http://192.168.0.194:8765` или Tailscale URL, если подключение не дома.
- Android app нужно настроить на Linux-сервер: Base URL `http://192.168.0.194:8765/` дома или `http://100.91.196.119:8765/` через Tailscale.
- Для внешнего доступа безопаснее использовать Tailscale/ZeroTier, а не открывать порт 8765 в интернет.

### Что отсутствует или стоит добить следующим шагом
- Автотесты API и Telegram callback-ов можно добавить отдельно, чтобы ловить 404/403 до деплоя.
- Нужна регулярная проверка Android build после изменений backend API.
- Нужна политика ротации логов и storage cleanup, чтобы медиа не забили диск.
- Нужно документировать конкретный формат agent tasks и response schema, если будет расти число команд.

## 11. Финальный вывод

- Главные файлы сервера: `backend/app/main.py`, `backend/app/config.py`, `backend/app/api/*`, `backend/app/services/*`.
- Главные файлы Telegram-бота: `backend/app/bot/runner.py`, `backend/app/bot/telegram_bot.py`, `backend/app/bot/lang_ru.py`.
- Главные файлы агента: `pc-agent/*`, особенно файлы подключения к серверу, задач, статуса, скриншотов и процессов.
- Главные файлы Android: `android-app/*`, особенно `ApiConfig.kt`, `ApiService.kt`, контейнер зависимостей, модели и экраны настроек/агентов/задач.
- Главные файлы Ubuntu-установки: `install_ubuntu.sh`, `systemd/pcmanager-server.service`, `systemd/pcmanager-bot.service`, `scripts/*.sh`.
- Нельзя удалять: `/etc/pcmanager/pcmanager.env`, `/var/lib/pcmanager/server.db`, `/var/lib/pcmanager/storage`, `/opt/pcmanager/venv` без понимания последствий, systemd service-файлы и backup-папки.
- Можно безопасно менять: `.env.example`, README, web panel, API/service modules через backup и перезапуск сервисов; реальные секреты менять только в `/etc/pcmanager/pcmanager.env`.

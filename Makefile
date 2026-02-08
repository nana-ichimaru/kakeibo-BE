# E2E（end-to-end）用の backend 環境を docker compose で立ち上げるための Makefile
# 使い方例:
#   make e2e-backend
#   make e2e-down

# docker compose の共通オプションをまとめた変数
# -p: compose project 名（コンテナ名/ネットワーク名などのprefixになる）
# -f: 使用する compose ファイル
# --env-file: compose に読み込ませる環境変数ファイル
COMPOSE = docker compose \
	-p kakeibo-be-test \
	-f docker-compose.test.yml \
	--env-file .env.test.e2e

# compose 内のサービス名（docker-compose.test.yml 側で定義されている想定）
TEST_API = test_api
TEST_DB  = test_db

# .PHONY: 同名のファイルが存在しても「ターゲットとして」必ず実行する宣言
.PHONY: e2e-down
e2e-down:
 	# E2E 用 compose を停止し、ボリュームも削除（DBのデータも消える）
	$(COMPOSE) down -v

.PHONY: e2e-up
e2e-up:
    # DB サービスをバックグラウンドで起動
	$(COMPOSE) up -d $(TEST_DB)
    # API サービスをバックグラウンドで起動
	$(COMPOSE) up -d $(TEST_API)

.PHONY: e2e-migrate
e2e-migrate:
 	# API コンテナ内で Alembic の migration を最新まで適用
    #  -c: alembic.ini のパスを指定
    # upgrade head: 最新リビジョンまでアップグレード
	$(COMPOSE) exec $(TEST_API) \
		alembic -c /kakeibo_be/alembic.ini upgrade head

.PHONY: e2e-backend
# e2e-backend は「依存ターゲット」を順に実行するまとめコマンド
# 1) 環境を一度落とす → 2) 起動する → 3) migrate を当てる
e2e-backend: e2e-down e2e-up e2e-migrate
    # 完了メッセージ（@ 付きなのでコマンド自体は表示されない）
	@echo "E2E backend ready on http://localhost:8001"

# make e2e-backendコマンドで実行できる

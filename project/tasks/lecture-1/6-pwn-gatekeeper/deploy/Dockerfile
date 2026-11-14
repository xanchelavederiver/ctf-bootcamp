# «Турникет» (pwn). Бинарь собирается внутри образа и запускается через socat:
# на каждое подключение — отдельный процесс gatekeeper.
FROM debian:12-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*
# Исходник берём из public/ — он выдаётся участнику, поэтому стенд собирается и у студента.
WORKDIR /build
COPY public/gatekeeper.c /build/
RUN gcc -fno-stack-protector -no-pie -O0 -o gatekeeper gatekeeper.c

FROM debian:12-slim
RUN apt-get update && apt-get install -y --no-install-recommends socat \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 ctf
COPY --from=build /build/gatekeeper /opt/gatekeeper/gatekeeper
USER ctf
EXPOSE 9001
CMD ["socat", "TCP-LISTEN:9001,reuseaddr,fork", "EXEC:/opt/gatekeeper/gatekeeper,stderr"]

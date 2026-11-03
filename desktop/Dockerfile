FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    VNC_PORT=5901 \
    NOVNC_PORT=6080 \
    DISPLAY=:1 \
    VNC_RESOLUTION=1280x800 \
    VNC_PW=cka \
    HOME=/home/candidate \
    USER=candidate

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl wget gnupg \
    xfce4 xfce4-terminal dbus-x11 \
    tigervnc-standalone-server tigervnc-common \
    novnc websockify \
    bash-completion procps \
    && rm -rf /var/lib/apt/lists/*

# Firefox from Mozilla APT (Ubuntu's firefox package is snap-based and unusable in containers)
RUN install -d -m 0755 /etc/apt/keyrings \
    && curl -fsSL https://packages.mozilla.org/apt/repo-signing-key.gpg \
      -o /etc/apt/keyrings/packages.mozilla.org.asc \
    && printf 'deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main\n' \
      > /etc/apt/sources.list.d/mozilla.list \
    && printf 'Package: *\nPin: origin packages.mozilla.org\nPin-Priority: 1000\n' \
      > /etc/apt/preferences.d/mozilla \
    && apt-get update \
    && apt-get install -y --no-install-recommends firefox \
    && rm -rf /var/lib/apt/lists/*

ARG KUBECTL_VERSION=v1.31.4
RUN curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl \
    && mkdir -p /etc/bash_completion.d \
    && kubectl completion bash > /etc/bash_completion.d/kubectl

RUN useradd -m -s /bin/bash candidate \
    && mkdir -p /home/candidate/.vnc /home/candidate/.kube /etc/firefox/policies \
    && chown -R candidate:candidate /home/candidate

COPY firefox-policies.json /etc/firefox/policies/policies.json
COPY xstartup /home/candidate/.vnc/xstartup
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /home/candidate/.vnc/xstartup /entrypoint.sh \
    && chown candidate:candidate /home/candidate/.vnc/xstartup

EXPOSE 6080
USER candidate
WORKDIR /home/candidate
ENTRYPOINT ["/entrypoint.sh"]

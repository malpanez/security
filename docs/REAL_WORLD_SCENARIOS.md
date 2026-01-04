# Real-World Scenarios (Estado real)

## Escenario 1: Sudoers monolítico

La mayoría de entornos mantienen todo en `/etc/sudoers`. El rol actual `sudoers_baseline` **solo aplica cambios si** `sudoers_baseline_strict=true` y siempre escribe:

- `/etc/sudoers`
- `/etc/sudoers.d/99-security`

**Implicación**: no hay modo híbrido ni preservación automática del archivo principal. Si necesitas migración gradual, gestiona `/etc/sudoers` externamente y habilita el rol solo cuando estés listo para reemplazarlo.

## Escenario 2: Múltiples instancias de SSH

`sshd_hardening` genera un único `/etc/ssh/sshd_config` y no gestiona múltiples instancias ni unidades systemd adicionales. Si tu entorno requiere instancias separadas (SFTP, DMZ, etc.), debes:

- crear unidades systemd propias,
- mantener `sshd_config` por instancia fuera del rol,
- usar el rol solo si aceptas que gestione el `sshd_config` principal.

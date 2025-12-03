.PHONY: lint test molecule install-local

lint:
	pre-commit run --all-files

molecule:
	molecule test -s default -c molecule/default/molecule.yml

sanity:
	ansible-test sanity --docker -v

# Instala la collection en una ruta local (para probarla con ansible-playbook)
install-local:
	rm -rf .collections
	mkdir -p .collections
	ansible-galaxy collection install -p .collections .

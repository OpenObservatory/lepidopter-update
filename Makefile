all:
	echo "nothing"

unittest:
	python updater/test_*.py

create-testvm:
	ansible-playbook -i deploy/inventory deploy/create-vm.yml

delete-testvm:
	ansible-playbook -i deploy/inventory deploy/delete-vm.yml

reset-testvm: delete-testvm create-testvm

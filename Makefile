ROOT_DIR=${PWD}
DTOOLS=${ROOT_DIR}/depot-tools

.DEFAULT_GOAL := help

# general
help:
	@echo "Type: make [rule]. Available options are:"
	@echo ""
	@echo "- help"
	@echo "- build-depot-tools"
	@echo "- build-pdfium"
	@echo "- build-ios"
	@echo "- submodule-update"
	@echo ""

build-ios:	
	rm -rf pdfium/out
	mkdir -p pdfium/out/Debug
	cd pdfium/ && ${DTOOLS}/gn args out/Debug	
	cd pdfium/ && ninja -C out/Debug pdfium_all
	cd pdfium/ && ${DTOOLS}/gn gen out/Debug

build-pdfium:
	rm -rf pdfium	
	${DTOOLS}/gclient config --unmanaged https://pdfium.googlesource.com/pdfium.git
	${DTOOLS}/gclient sync
	cd pdfium
	./build/install-build-deps.sh
	
build-depot-tools:
	rm -rf depot-tools
	git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git depot-tools

submodule-update:
	git submodule update --recursive --remote

ARCH_LIBDIR ?= /lib/$(shell $(CC) -dumpmachine)

SGX_SIGNER_KEY ?= ../../Pal/src/host/Linux-SGX/signer/enclave-key.pem

BLENDER_DIR = $(PWD)/blender_dir
BLENDER_SRC ?= blender-2.82-linux64.tar.xz
BLENDER_MIRRORS ?= \
    https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.82 \
    https://packages.gramineproject.io/distfiles
BLENDER_SHA256 ?= b13600fa2ca23ea1bba511e3a6599b6792acde80b180707c3ea75db592a9b916
BLENDER_VER = 2.82

DATA_DIR = $(PWD)/data
RUN_DIR = $(PWD)/run_dir

UBUNTU_VER = $(shell lsb_release --short --id)$(shell lsb_release --short --release)

ifeq ($(DEBUG),1)
GRAMINE_LOG_LEVEL = debug
else
GRAMINE_LOG_LEVEL = error
endif

.PHONY: all
all: python.manifest $(BLENDER_DIR)/blender
ifeq ($(SGX),1)
all: python.manifest.sgx python.sig python.token
endif

python.manifest: python.manifest.template
	gramine-manifest \
		-Dlog_level=$(GRAMINE_LOG_LEVEL) \
		-Darch_libdir=$(ARCH_LIBDIR) \
		-Ddata_dir=$(DATA_DIR) \
		-Dblender_dir=$(BLENDER_DIR) \
		-Dblender_ver=$(BLENDER_VER) \
		-Dentrypoint=$(realpath $(shell sh -c "command -v python3")) \
		$< >$@

python.manifest.sgx: python.manifest
	@test -s $(SGX_SIGNER_KEY) || \
	    { echo "SGX signer private key was not found, please specify SGX_SIGNER_KEY!"; exit 1; }
	gramine-sgx-sign \
		--key $(SGX_SIGNER_KEY) \
		--manifest $< \
		--output $@

python.sig: python.manifest.sgx

python.token: python.sig
	gramine-sgx-get-token --output $@ --sig $<

$(BLENDER_DIR)/blender:
	../common_tools/download --output blender.tar.xz --sha256 $(BLENDER_SHA256) \
		$(foreach mirror,$(BLENDER_MIRRORS),--url $(mirror)/$(BLENDER_SRC))
	mkdir $(BLENDER_DIR)
	tar -C $(BLENDER_DIR) --strip-components=1 -xf blender.tar.xz

$(RUN_DIR):
	mkdir -p $@

$(DATA_DIR)/images:
	mkdir -p $@

.PHONY: clean
clean:
	$(RM) *.manifest *.manifest.sgx *.token *.sig OUTPUT* *.PID TEST_STDOUT TEST_STDERR
	$(RM) -r scripts/__pycache__
	$(RM) -r \
		$(RUN_DIR) $(DATA_DIR)/images blender.manifest blender.manifest.sgx blender.sig \
		blender.token

.PHONY: distclean
distclean: clean
	$(RM) -r $(BLENDER_DIR) blender.tar.xz

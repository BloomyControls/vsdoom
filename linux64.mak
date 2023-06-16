# Auto-generated 64-bit Linux Makefile for vsdoom.
#
# Generated Fri Jun 16 14:07:07 2023

# change this if you wish to update the veristand version used
# (this is overridden by the value in build_linux64.bat)
VERISTAND_VERSION ?= 2020

CC = x86_64-nilrt-linux-gcc.exe
CXX = x86_64-nilrt-linux-g++.exe

# GCCSYSROOTPATH is generated from NI's bat files
CXXFLAGS += -MMD -MP -fPIC -std=c++14 \
	--sysroot="$(subst \,/,$(GCCSYSROOTPATH))" -fstrength-reduce \
	-Os -fno-builtin -fno-strict-aliasing

CFLAGS += -MMD -MP -fPIC -std=gnu11 \
	--sysroot="$(subst \,/,$(GCCSYSROOTPATH))" -fstrength-reduce \
	-Os -fno-builtin -fno-strict-aliasing

CPPFLAGS += -DkNIOSLinux -DNORMALUNIX

RM := cs-rm -rf

LDFLAGS += -fPIC -lrt -lpthread -lm -lc \
	--sysroot="$(subst \,/,$(GCCSYSROOTPATH))"

# add include directories (-I/path/to/dir) here
INCLUDES := -Isrc

# include directory for ni_modelframework.h
NIVS_INC := "-IC:/VeriStand/$(VERISTAND_VERSION)/ModelInterface"

# override this with environment variable if desired
BUILDDIR ?= build/linux64

SRC := $(wildcard src/*.c) $(wildcard src/device/*.c)
OBJ := $(patsubst src/%,$(BUILDDIR)/%.o,$(SRC))
DEP := $(wildcard $(BUILDDIR)/*.d)

NIVS_SRC := C:/VeriStand/$(VERISTAND_VERSION)/ModelInterface/custom/src/ni_modelframework.c
NIVS_OBJ := $(BUILDDIR)/ni_modelframework.o

TARGET := $(BUILDDIR)/libvsdoom64.so

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJ) $(NIVS_OBJ)
	@echo LINK	$@
	@$(CXX) $(LDFLAGS) -shared -m64 -Wl,-soname,"$(@F)" -o "$@" $^

-include $(DEP)

$(NIVS_OBJ): $(NIVS_SRC) | $(BUILDDIR)
	@echo CC	$@
	@$(CC) $(CFLAGS) $(CPPFLAGS) -D_XOPEN_SOURCE=700 -w "-Isrc" $(NIVS_INC) -o "$@" -c "$<"

define GEN_OBJ_TARGET
$$(BUILDDIR)/%$(1).o: src/%$(1) | $$(BUILDDIR)
	@echo $(2)	$$@
	@$$($(2)) $$($(3)) $$(CPPFLAGS) $$(INCLUDES) $$(NIVS_INC) -o "$$@" -c "$$<"
endef

$(eval $(call GEN_OBJ_TARGET,.c,CC,CFLAGS))
$(eval $(call GEN_OBJ_TARGET,.cpp,CXX,CXXFLAGS))
$(eval $(call GEN_OBJ_TARGET,.cc,CXX,CXXFLAGS))
$(eval $(call GEN_OBJ_TARGET,.cxx,CXX,CXXFLAGS))

$(BUILDDIR):
	@echo MKDIR	$@
	@mkdir "$@"
	@echo MKDIR	$@/device
	@mkdir "$@/device"

clean:
	@echo RM	$(BUILDDIR)
	@$(RM) -rf "$(BUILDDIR)"

# options de compilation
APIDIR = -I${C_API_CLIENT} -I${C_API_APPLI}
CC = gcc
CCFLAGS = -std=c99 -Wall $(APIDIR)
LIBS = -L${C_LIB}
LDFLAGS = -lm -lcgs

# fichiers du projet
SRC = template.c
OBJ = $(SRC:.c=.o)
EXEC = main
MFILE = makefile.generic

# fichiers de la lib
LIBSRC = networksAPI.c clientAPI.c
LIBOBJ = $(LIBSRC:.c=.o)
LIBNAME = libcgs.a
LIBHEAD = ${C_API_CLIENT}/ret_type.h ${C_API_APPLI}/networksAPI.h

# règle initiale
all: $(EXEC)

#lib
lib: $(LIBNAME)

distrib: $(LIBNAME) $(SRC) $(MFILE)
	mkdir -p ${C_SRC}
	cp -f $(SRC) ${C_SRC}
	sed 's!^APIDIR!APIDIR = '${C_INC}'!' $(MFILE) > tmp
	sed 's!^LIBS!LIBS = -L'${C_LIB}'!' tmp > tmp2
	sed 's!^SRC!SRC = '$(SRC)'!' tmp2 > $(C_SRC)/makefile
	rm -f tmp tmp2

$(LIBNAME): $(LIBOBJ) $(LIBHEAD)
	echo $(LIBOBJ)
	ar r $@ $^
	ranlib $@
	mkdir -p ${C_LIB}
	cp $@ ${C_LIB}
	mkdir -p ${C_INC}
	cp $(LIBHEAD) ${C_INC}


# dépendance des .h
main.o: $(LIBNAME)
networksAPI.o: clientAPI.h networksAPI.h ret_type.h
clientAPI.o : clientAPI.h ret_type.h


networksAPI.h:
	ln -sf ${C_API_APPLI}/$@

clientAPI.h:
	ln -sf ${C_API_CLIENT}/$@

networksAPI.c:
	ln -sf ${C_API_APPLI}/$@

clientAPI.c:
	ln -sf ${C_API_CLIENT}/$@

ret_type.h:
	ln -sf ${C_API_CLIENT}/$@

# règles de compilation
%.o: %.c
	$(CC) $(CCFLAGS) -o $@ -c $<

# règles d'édition de liens
$(EXEC): $(OBJ)
	$(CC) -o $@ $^ $(LIBS) $(LDFLAGS)

# règles supplémentaires
clean:
	rm -f *.a *.o *~ ${C_LIB}/* ${C_INC}/* ${C_SRC}/*
rmproper:
	rm -f $(EXEC) *.o

# options de compilation
APIDIR = ../API
CC = gcc
CCFLAGS = -Wall -I $(APIDIR)
LIBS =
LDFLAGS = -lm

# fichiers du projet
SRC = template.c
OBJ = $(SRC:.c=.o)
EXEC = main


# règle initiale
all: $(EXEC)

# dépendance des .h
main.o:

# règles de compilation
%.o: %.c
	$(CC) $(CCFLAGS) -o $@ -c $<

# règles d'édition de liens
$(EXEC): $(OBJ)
	$(CC) -o $@ $^ $(LIBS) $(LDFLAGS)

# règles supplémentaires
clean:
	rm -f *.o *~
rmproper:
	rm -f $(EXEC) *.o

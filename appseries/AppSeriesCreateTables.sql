

CREATE TABLE Serie ( 
	SerieId INT PRIMARY KEY,
	Nombre TEXT NOT NULL,
	Descripcion TEXT NOT NULL,
	Imagen TEXT NOT NULL,
	Genero TEXT NOT NULL,
	FechaEmision TEXT NOT NULL,
	Estado TEXT NOT NULL);


CREATE TABLE Capitulo ( CapituloId INT PRIMARY KEY,
	Temporada INT NOT NULL,
	Numero INT NOT NULL,
	Titulo TEXT NOT NULL);

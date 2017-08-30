# ###########################################################################################
# Name: pixelToTable
# Descripcion: Script que permite obtener los valores de pixel de una o mas imagenes utilizando,
# una entidad geometrica de uno o mas puntos.
# SERNAGEOMIN, mayo 2017
# ###########################################################################################

# -*- coding: utf-8 -*-
import arcpy, os, sys, time, traceback
import datetime

arcpy.env.addOutputsToMap = 0 #que no agregue al mapa
arcpy.env.overwriteOutput = 1 #sobreescribir

class LicenseError(Exception):
	pass

def delDirectory(pathBorrar):
	try:
		arcpy.Delete_management(pathBorrar)
		arcpy.AddMessage("El directorio existente junto con sus archivos ha sido borrado")
	except:
		e = sys.exc_info()[1]
		arcpy.AddError(e.args[0])
		arcpy.AddMessage("No fue posible eliminar el directorio")
		sys.exit(0)

def validate(date_text, formato):
	try:
		datetime.datetime.strptime(date_text, formato)
		return True
	except:
		e = sys.exc_info()[1]
		arcpy.AddError(e.args[0])
		arcpy.AddMessage("El formato fecha no corresponde al formato de fecha definido")
		return False

def raster_finder(workspace_path):

	try:
		old_workspace = arcpy.env.workspace

		def find_rasters(workspace):
			arcpy.env.workspace = workspace
			rasterds = arcpy.ListRasters("","TIF")
			arcpy.AddMessage("mostrando rasters identificados: ")
			for ras in rasterds:
				arcpy.AddMessage(ras)
				yield os.path.join(workspace, ras), ras
			# recursivamente busca a través de todos los directorios
			subws = arcpy.ListWorkspaces()
			for new_workspace in subws:
				for pathRas, ras in find_rasters(new_workspace):
					yield pathRas, ras

		for pathRas, ras in find_rasters(workspace_path):
			yield pathRas, ras

		arcpy.env.workspace = old_workspace
	except:
		e = sys.exc_info()[1]
		arcpy.AddError(e.args[0])
		arcpy.AddMessage("Ha fallado la busqueda de rasters")

def getTablaRaster(ruta, proj, tblIndice, fldIndice, fldNombre, fldRuta, formatFecha, horas, pref, suf):
	try:
		arcpy.AddMessage("Escaneando la ruta de mosaico...")
		cursorTabla = arcpy.da.InsertCursor(tblIndice,[fldIndice, fldNombre, fldRuta])
		for rasPath, rasName in raster_finder(ruta):
		   # Se excluyen raster dataset que no tengan georreferencia
			desc = arcpy.Describe(rasPath)
			indice = rasName[int(pref):int(suf)].replace("S","")
			if not validate(indice, formatFecha):
				mensaje = "Formato de fecha no valido, revise el nombre del raster, error"
				arcpy.AddMessage(mensaje)
				return mensaje
			else:
				corrHoras = datetime.timedelta(hours = int(horas))
				indiceDate = datetime.datetime.strptime(indice, formatFecha)
				indiceLocal = indiceDate - corrHoras
				indiceFinal = indiceLocal.strftime(formatFecha)
			if desc.SpatialReference.Name.lower() == "unknown":
				arcpy.DefineProjection_management(rasPath, proj)
			cursorTabla.insertRow([indiceFinal, rasName, rasPath])
		mensaje = "Obtención de lista de rasters exitosa"
		del cursorTabla
		return mensaje
	except:
		e = sys.exc_info()[1]
		arcpy.AddError(e.args[0])
		arcpy.AddMessage("No se ha podido obtener la lista de nombres")
		mensaje = "error"
		return mensaje

def main(*argv):
	#asignacion de parametros. El índice del arreglo debe coincidir con el orden definido
	#en el cuadro de diálogo de de arcmap.
	pathRaster = argv[0]
	ptoMuestra = argv[1]
	fldIdentificador = argv[2]
	output_path = argv[3]
	nomFolder = argv[4]
	nomEntidadSalida = argv[5]
	factorEscala = argv[6]
	path_log = argv[7]
	horasLocal = argv[8]
	prefNom = argv[9]
	sufNom = argv[10]

	try:
		#Evaluando si existe licencia de arcEditor
		if str(arcpy.CheckOutExtension("Spatial")) != 'Unavailable':
			arcpy.AddMessage("Extension Spatial Analyst disponible")
		else:
			raise LicenseError

		arcpy.AddMessage("Declaracion de variables")
		#Declarando parametros de formato fecha
		formatDate = "%Y%m%d-%H%M"
		#Declarando parametros de la tabla
		tblIndice = "tablaIndice"
		fldCodigo = 'CODIGO'
		tamFLDcod = 30
		fldRaster = 'NOM_RASTER'
		tamFLDraster = 250
		fldPathRaster = 'RUTA_RASTER'
		tamFLDpathRaster = 300
		#Declarando path de trabajo
		nomFGDB = "resultados.gdb"
		pathResultado = os.path.join(output_path, nomFolder)
		pathFGDB = os.path.join(pathResultado, nomFGDB)
		pathTabla = os.path.join(pathFGDB, tblIndice)
		pathMuestra = os.path.join(pathFGDB, nomEntidadSalida)
		coor_system = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
		#Declarando parametros del log
		nomLog = 'pixelToPoint'
		extenLog = '.log'
		nomFile = str(time.strftime("%Y-%m-%d_%H.%M.%S") + nomLog + extenLog)

		arcpy.AddMessage("Creando archivo de log de ejecucion...")
		fileLog = os.path.join(path_log,nomFile)
		#creando y abriendo archivo
		outfile = open(fileLog,'w')
		outfile.writelines('LOG DE EJECUCION' + '\n')
		outfile.writelines('Parametros:' + '\n')
		outfile.writelines('Ruta de rasters: ' + str(pathRaster) + '\n')
		outfile.writelines('Entidad de puntos de muestreo: ' + str(ptoMuestra) + '\n')
		outfile.writelines('Campo que identificaran los puntos en los resultados: ' + str(fldIdentificador) + '\n')
		outfile.writelines('Ruta de salida: ' + str(output_path) + '\n')
		outfile.writelines('Nombre de entidad resultante: ' + str(nomEntidadSalida) + '\n')
		outfile.writelines('Directorio del Log: ' + str(path_log) + '\n\n')
		outfile.writelines('Resultados: ' + '\n')

		#validando puntos de muestreo
		if long(arcpy.GetCount_management(ptoMuestra).getOutput(0)) == 0:
			arcpy.AddMessage("No se encontraron geometrias de muestreo, la ejecucion ha terminado")
			outfile.writelines('No se encontraron geometrias de muestreo, la ejecucion ha terminado' + '\n')
			outfile.close()
			sys.exit(0)

		arcpy.AddMessage("Creando directorio y fGDB de resultados")
		if os.path.exists(output_path):
			#eliminando carpeta de resultado
			if os.path.exists(pathResultado):
				delDirectory(pathResultado)
			#Creando directorios resultado
			os.makedirs(pathResultado)
			outfile.writelines('Directorio de resultados creado con exito' + '\n')
			arcpy.CreateFileGDB_management(pathResultado, nomFGDB)
			outfile.writelines('Geodatabase creada con exito' + '\n')
		else:
			arcpy.AddMessage("La ruta especificada no existe, no fue posible crear el directorio o FGDB necesaria")
			outfile.writelines('La ruta especificada no existe, no fue posible crear el directorio o FGDB necesaria' + '\n')
			sys.exit(0)

		try:
			arcpy.AddMessage("Transformando capa de puntos a WGS84")
			arcpy.AddMessage("ruta de muestreo: " + pathMuestra)
			arcpy.Project_management(ptoMuestra, pathMuestra, coor_system)
			outfile.writelines('capa de puntos transformada correctamente' +'\n')

			arcpy.AddMessage("Eliminando campos innecesarios")
			listFld = arcpy.ListFields(pathMuestra)
			for field in listFld:
				if not field.required and field.name != fldIdentificador:
					arcpy.DeleteField_management(pathMuestra,field.name)
			outfile.writelines('Campos innececerios eliminados correctamente' +'\n')
		except:
			e = sys.exc_info()[1]
			arcpy.AddError(e.args[0])
			outfile.writelines('No se pudo transformar capa de puntos de entrada o eliminar campos innececerios' +'\n')
			sys.exit(0)

		#Creando tabla indice
		arcpy.CreateTable_management(pathFGDB, tblIndice)
		arcpy.AddField_management(pathTabla, fldCodigo, "TEXT", "", "", tamFLDcod)
		arcpy.AddField_management(pathTabla, fldRaster, "TEXT", "", "", tamFLDraster)
		arcpy.AddField_management(pathTabla, fldPathRaster, "TEXT", "", "", tamFLDpathRaster)

		arcpy.AddMessage("Creando tabla de rasters")
		mensaje = getTablaRaster(pathRaster, coor_system, pathTabla, fldCodigo, fldRaster, fldPathRaster, formatDate, horasLocal, prefNom, sufNom)

		if "error" in mensaje:
			arcpy.AddMessage("La lectura de archivos rasters ha fracasado")
			outfile.writelines('La lectura de archivos rasters ha fracasado ' + '\n' + mensaje)
			sys.exit(0)

		arcpy.AddMessage("Verificando rutas identificadas")
		cantRaster = long(arcpy.GetCount_management(pathTabla).getOutput(0))
		if cantRaster == 0:
			arcpy.AddMessage("No se encontraron rasters en el directorio ingresado")
			outfile.writelines('No se encontraron rasters en el directorio ingresado' + '\n')
			outfile.close()
			sys.exit(0)
		else:
			arcpy.AddMessage("numero de rasters identificados: " + str(cantRaster))
			outfile.writelines('numero de rasters identificados: ' + str(cantRaster) + '\n')

		arcpy.AddMessage("Iniciando lectura de muestras")
		with arcpy.da.SearchCursor(pathTabla, [fldCodigo, fldRaster, fldPathRaster]) as cursorRaster:
			for elemRaster in cursorRaster:
				try:
					arcpy.AddMessage("Calculando valores para raster: " + str(elemRaster[1]))
					arcpy.sa.ExtractMultiValuesToPoints(pathMuestra,[[elemRaster[2], elemRaster[0]]])
					fldFecha = elemRaster[0]
					campo = "F" + fldFecha.replace("-","_")
					campo_calc = campo + "C"
					arcpy.AddField_management(pathMuestra, campo_calc, "DOUBLE")
					expresion = "!" + campo + "!/" + factorEscala + ".0"
					arcpy.CalculateField_management(pathMuestra, campo_calc, expresion, "PYTHON_9.3")
					campoAlias = fldFecha[0:-9] + "/" + fldFecha[4:-7] + "/" + fldFecha[6:-5] + " " + fldFecha[9:-2] + ":" + fldFecha[11:]
					arcpy.AddMessage("Asignando alias")
					arcpy.DeleteField_management(pathMuestra, campo)
					arcpy.AlterField_management(pathMuestra, campo_calc, "", campoAlias)
					outfile.writelines('Obtencion de valores pixel de forma correcta para: ' + elemRaster[1] + '\n')
				except:
					e = sys.exc_info()[1]
					arcpy.AddError(e.args[0])
					outfile.writelines('No se pudo calcular valores pixel, para el raster' + str(elemRaster[1]) +'\n')
		arcpy.DeleteField_management(pathTabla, fldRaster)

		outfile.close()
		arcpy.AddMessage("Archivo cerrado exitosamente")
	except LicenseError:
		arcpy.AddMessage("Extension Spatial Analyst no disponible")
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError(e.args[0])
		arcpy.AddMessage("Geoproceso de obtencion de valores de pixel a punto ha fallado, incidencia no controlada")
		outfile.writelines('Geoproceso de obtencion de valores de pixel a punto ha fallado, incidencia no controlada')
		outfile.close()

if __name__ == "__main__":
	#Creando arreglo de parámetros de ingreso
	argv = tuple(arcpy.GetParameterAsText(i)
				 for i in range(arcpy.GetArgumentCount()))
	main(*argv)

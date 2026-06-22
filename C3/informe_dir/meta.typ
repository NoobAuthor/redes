#import "@preview/minerva-report-fcfm:0.2.2" as minerva

#let titulo = "Forwarding Básico y Fragmentación IP"
#let subtitulo = ""
#let tema = ""

#let departamento = minerva.departamentos.dcc
#let curso = "CC4303 - Redes"

#let fechas = (
  realización: "21 de Junio de 2026",
  entrega: minerva.formato-fecha(datetime.today())
)
#let lugar = "Santiago, Chile"

#let autores = "Igor Assis Passos de Souza, Nelson A. Navarro B."
#let equipo-docente = (
  Profesores: " Ivana Bachmann",
)

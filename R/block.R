
INPUT.FILE <- 'input/2016/2016_03.csv'
OUTPUT.FILE <- "output/2015_W/%s_%s_%s.txt"

x <- read.csv(INPUT.FILE, header=T, sep=';')
ncol(x)
nrow(x)
colnames(x) <- c(
  "NUM", 
  "SIT", 
  "DATA", 
  "ORG.PREV", 
  "DES.PREV", 
  "ORG.OPR", 
  "DES.OPR", 
  "DATA.PREV.OUT", 
  "HORA.PREV.OUT", 
  "DATA.OPR.OUT", 
  "OUT", 
  "DEP", 
  "ORG.DELAY", 
  "ORG.STATUS", 
  "DATA.PREV.ARR", 
  "HORA.PREV.ARR", 
  "DATA.OPR.ARR", 
  "ARR", 
  "IN", 
  "DES.DELAY", 
  "DES.STATUS", 
  "X0", 
  "X1", 
  "X2", 
  "FT", 
  "BT", 
  "EQP", 
  "TAIL", 
  "CFG", 
  "PAX", 
  "LF", 
  "COD1", 
  "TEMPO1", 
  "COD2", 
  "TEMPO2"
)

ToDecimal <- function(x, col) {
  # Converte uma coluna de valores de tempo no formato [h]:mm em um vetor de decimais
  #boxplo
  # Args:
  #     x: data frame
  #   col: nome da coluna no data frame
  #
  # Returns: vetor de decimais
  #
  vec <- as.character(x[, col])
  sapply(strsplit(vec, ":"), function(x) {
    x <- as.numeric(x)
    x[1] + x[2] / 60
  })
}

GetRouteData <- function(x, col, from, to, r.out = FALSE) {
  # Obtém dados da coluna referente a um dado par de aeroportos
  #
  # Args:
  #     x: data frame
  #   col: nome da coluna no data frame
  #  from: aeroporto de saída
  #    to: aeroporto de chegada  
  # r.out: remover outliers?
  #
  # Returns: vetor com dados da coluna
  #
  y <- x[x$SIT != "CNL" & x$ORG.PREV == from & x$ORG.OPR == from & x$DES.PREV == to & x$DES.OPR == to, col]
  if (r.out) {
    y[!y %in% boxplot.stats(y)$out]
  }
  else {
    y
  }
}

GetOrgData <- function(x, col, from, r.out = FALSE) {
  # Obtém dados da coluna referente a um dado aeroporto de saída
  #
  # Args:
  #     x: data frame
  #   col: nome da coluna no data frame
  #  from: aeroporto de saída
  #    to: aeroporto de chegada  
  # r.out: remover outliers?
  #
  # Returns: vetor com dados da coluna
  #
  y <- x[x$SIT != "CNL" & x$ORG.PREV == from & x$ORG.OPR == from, col]
  if (r.out) {
    y[!y %in% boxplot.stats(y)$out]
  }
  else {
    y
  }
}

GetDesData <- function(x, col, to, r.out = FALSE) {
  # Obtém dados da coluna referente a um dado aeroporto de saída
  #
  # Args:
  #     x: data frame
  #   col: nome da coluna no data frame
  #  from: aeroporto de saída
  #    to: aeroporto de chegada  
  # r.out: remover outliers?
  #
  # Returns: vetor com dados da coluna
  #
  y <- x[x$SIT != "CNL" & x$DES.PREV == to & x$DES.OPR == to, col]
  if (r.out) {
    y[!y %in% boxplot.stats(y)$out]
  }
  else {
    y
  }
}

WriteRouteData <- function(x, col, from, to, r.out = FALSE, append = FALSE) {
  # Escreve em arquivo dados da coluna referente a um dado par de aeroportos
  #
  # Args:
  #      x: data frame
  #    col: nome da coluna no data frame
  #   from: aeroporto de saída
  #     to: aeroporto de chegada  
  #  r.out: remover outliers?
  # append: anexar no arquivo já criado
  #
  # Returns: 
  #
  f.name <- sprintf(OUTPUT.FILE, from, to, col)
  d <- GetRouteData(x, col, from, to, r.out)
  write(d, file = f.name, ncolumns = 1, append = append)
}

WriteAllRoutesData <- function(x, col, r.out = FALSE, append = FALSE) {
  # Escreve em arquivo dados da coluna referente a todos os pares de aeroportos
  #
  # Args:
  #      x: data frame
  #    col: nome da coluna no data frame
  #   from: aeroporto de saída
  #     to: aeroporto de chegada  
  #  r.out: remover outliers?
  # append: anexar no arquivo já criado
  #
  # Returns: 
  #
  for (from in levels(x$ORG.PREV)) {
    des <- factor(x[x$ORG.PREV == from, "DES.PREV"])
    for (to in levels(des)) {
      WriteRouteData(x, col, from, to, r.out, append)
    }
  }
}

out.dec <- ToDecimal(x, "OUT")
dep.dec <- ToDecimal(x, "DEP")
arr.dec <- ToDecimal(x, "ARR")
in.dec  <- ToDecimal(x, "IN")

x$TAXI.OUT <- 60 * sapply(dep.dec - out.dec, function(x){ ifelse(x < 0, x + 24, x) })
x$TAXI.IN  <- 60 * sapply(in.dec - arr.dec, function(x){ ifelse(x < 0, x + 24, x) })
x$BT.DEC   <- ToDecimal(x, "BT")
x$FT.DEC   <- ToDecimal(x, "FT")


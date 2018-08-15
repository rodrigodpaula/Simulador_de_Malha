library(qcc)

#### Entradas

args <- commandArgs(trailingOnly=T)

plot.file <- 'plots.pdf'

if (length(args) != 5) {
    cat('Uso: Rscript crew.R <legs1.csv> <name1> <legs2.csv> <name2> <cutoff>\n')
    stop()
} else {
    file1 <- args[1]
    name1 <- args[2]
    file2 <- args[3]
    name2 <- args[4]
    cutoff <- as.integer(args[5])
}

##### Funções

GetCrewDelayTimes <- function(x, cutoff=5, size=15) {
    bases = c()
    count = c()
    list <- levels(x$ORG)
    for (b in list) {
        rows <- nrow(x[x$ORG == b & x$ORG.DELAY > cutoff & x$CODE == 'CR', ])
        if (rows > 0) {
            bases <- append(bases, b)
            count <- append(count, rows)
        }
    }
    names(count) <- bases
    return (sort(count, decreasing=T)[1:min(length(count), size)])
}

#### Inicialização

pdf(plot.file)

cnames <- c(
    "ROUTE",
    "FLEET",
    "NUMBER",
    "ORG",
    "DES",
    "SDT",
    "SAT",
    "P.BLOCK",
    "ADT",
    "AAT",
    "E.BLOCK",
    "CODE",
    "ORG.DELAY",
    "DES.DELAY",
    "PL.CNX",
    "PR.CNX",
    "EX.CNX",
    "CR.ROUTE",
    "CR.FLEET",
    "CR.NUMBER",
    "CR.ORG",
    "CR.DES",
    "CR.SDT",
    "CR.SAT",
    "CR.ADT",
    "CR.AAT"
)

x1 <- read.csv(file1, header=T, sep=';')
x2 <- read.csv(file2, header=T, sep=';')

colnames(x1) <- cnames
colnames(x2) <- cnames

#### Atrasos na Saída

cat('==========================================================================\n')
cat('Atrasos na Saída Tripulação\n')
cat('==========================================================================\n\n')

dep1 <- x1[x1$CODE == 'CR', 'ORG.DELAY']
dep2 <- x2[x2$CODE == 'CR', 'ORG.DELAY']
per1 <- 100 * length(dep1) / nrow(x1)
per2 <- 100 * length(dep2) / nrow(x2)
del1 <- sum(dep1) / nrow(x1)
del2 <- sum(dep2) / nrow(x1)
cat(sprintf('Total %s = %d (%5.2f%%)\n', name1, length(dep1), per1))
cat(sprintf('Total %s = %d (%5.2f%%) [Delta = %5.2f%%]\n', name2, length(dep2), per2, 100 * (per2 - per1) / per1))
cat(sprintf('Atrasado médio %s = %5.3f\n', name1, del1))
cat(sprintf('Atrasado médio %s = %5.3f [Delta = %5.2f%%]\n', name2, del2, 100 * (del2 - del1) / del1))
print(t.test(dep1, dep2))
boxplot(dep1, dep2, names=c(name1, name2), col=c('orange', 'green'), main='Atraso na Saída (Crew Connection)', ylab='Atraso (min)')
dep1 <- GetCrewDelayTimes(x1, cutoff=cutoff, size=15)
dep2 <- GetCrewDelayTimes(x2, cutoff=cutoff, size=15)
pareto.chart(dep1, main=sprintf('Atrasos (Crew Connection) > %d na Saída: %s', cutoff, name1), ylab='Total', ylab2='', cex.names=0.8)
pareto.chart(dep2, main=sprintf('Atrasos (Crew Connection) > %d na Saída: %s', cutoff, name2), ylab='Total', ylab2='', cex.names=0.8)

dev.off()
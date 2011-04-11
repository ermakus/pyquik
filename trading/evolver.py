from pyevolve import G1DList
from pyevolve import GAllele
from pyevolve import GSimpleGA
from pyevolve import Selectors
from pyevolve import Statistics
from pyevolve import Scaling
from pyevolve import Mutators
from pyevolve import Initializators
from pyevolve import DBAdapters

from trading.backtest import BacktestMarket
from trading.strategy import Strategy

class Evolver:
    def __init__(self,filename):
        self.filename = filename

    def fitness(self, genome):
        print(genome)
        market = BacktestMarket()
        market.add_strategy( Strategy( "Bankruptsy", [market["SBER"]], genome[1] ) )
        market.load( self.filename )
        return market.balance

    def run(self):
        # Allele define valid chromosome value
        alleles = GAllele.GAlleles()

        # Define gene with 2 chromosomes
        # MA type
        alleles.add(GAllele.GAlleleList([0,1,2,3,4]))
        # MA range
        alleles.add(GAllele.GAlleleRange(1, 99))
        # MA condition
        alleles.add(GAllele.GAlleleList(["<",">","="]))
      
        # Genome instance, 1D List
        genome = G1DList.G1DList(len(alleles))
        # Sets the range max and min of the 1D List
        genome.setParams(allele=alleles)
        # The evaluator function (evaluation function)
        genome.evaluator.set(self.fitness)
        # This mutator and initializator will take care of
        # initializing valid individuals based on the allele set
        # that we have defined before
        genome.mutator.set(Mutators.G1DListMutatorAllele)
        genome.initializator.set(Initializators.G1DListInitializatorAllele)

        # Genetic Algorithm Instance
        ga = GSimpleGA.GSimpleGA(genome)
        # Set the Roulette Wheel selector method, the number of generations and
        # the termination criteria
        ga.selector.set(Selectors.GRouletteWheel)
        ga.setGenerations(10)
        ga.setPopulationSize(10)
        ga.terminationCriteria.set(GSimpleGA.ConvergenceCriteria)

        pop = ga.getPopulation()
        pop.scaleMethod.set(Scaling.SigmaTruncScaling)

        ga.evolve(freq_stats=10)
        # Best individual
        print( ga.bestIndividual() )


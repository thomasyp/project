import os
from lf1.control_rod import ControlRod
from tool.handle_mcnpinp import McnpinpHandler
from tool.mcnp_reader import McnpTallyReader
from tool.self_defined_exception import CustomError


class SearchRodCriticalPos(object):
    def __init__(self):
        self.mh = McnpinpHandler()
        self.mtr = McnpTallyReader()
    
    def preProcessing(self, mcnpfile, rod_postion, rods):
        self.mh.cleanup(mcnpfile)
        for key, rod in rods.items():
            print(key)
            print(type(rod))
            rod.setInsertPosition(rod_postion)
            self.mh.modifyinp(mcnpfile, rod.getTrCardNo(), rod.ouputforMcnpinp(), section='data')

    def postProcessing(self, mcnpfile, outfilename):
        outputfile = ''.join([mcnpfile, 'o'])
        if os.path.isfile(outputfile):
            print('MCNP5 run finished!')
            keff = self.mtr.readKeff(outputfile)['keff']
            self.mh.deleteFiles(outfilename)
            os.rename(outputfile, outfilename)    
        else:
            raise CustomError('MCNP5 did not run successful!')
        return keff

    def startSearch(self, mcnpfile, num_node=1, num_processor=16, reference_keff=1.0, eps=1e-4, **rods):
        inputfile = mcnpfile
        for key, rod in rods.items():
            if type(rod) != ControlRod:
                raise TypeError('The function parameter requires an instance of class ControlRod!')
            else:
                rod_range = rod.getRodRange()

        low = 0
        high = rod_range
        with open('results.out', 'w') as fid:
            fid.write('{:^12} {:^10}\n'.format('Rod position', 'keff'))

        while high - low > 0.1:
            mid = (low + high)/2.0
            self.preProcessing(inputfile, mid, rods)             

            os.system('  mpirun -r ssh -np '+str(int(num_node*num_processor))
                         +' /home/daiye/bin/mcnp5.mpi n='+inputfile)
            # os.system('  mcnp5 '+' n='+inputfile)
            keff = self.postProcessing(inputfile, ''.join([inputfile, 'o', str(mid)]))
            with open('results.out', 'a') as fid:
                fid.write('{:^12.6f} {:^10.5f}\n'.format(mid, keff))
            if abs(keff - reference_keff) < eps:
                return mid
            if keff > reference_keff:
                high = mid
            else:
                low = mid
                    
        return -1
        

if __name__ == '__main__':
    rod1 = ControlRod(rod="3#", trCard='tr3', rodRange=180.0, rodXCoordinate=-30.2514162, rodYCoordinate=0)
    rod2 = ControlRod(rod="5#", trCard='tr5', rodRange=180.0, rodXCoordinate=15.1257072, rodYCoordinate=-26.1984933)
    src = SearchRodCriticalPos()
    src.startSearch('0000', rod1=rod1, rod2=rod2)
    

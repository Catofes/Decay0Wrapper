#!/bin/python2
import math
import scipy.integrate as integrate
import scipy.special as function

pi = 3.1415927
emass = 0.51099906

dshelp_dens = 0
dshelp_denf = 0


class Generate():
    def __init__(self):
        self.d = {}
        # i2bbs
        self.process_name = None
        # chnuclide
        self.particle_type = None
        self.energy_levels_info = None
        # ilevel
        self.energy_level = None
        self.bb_decay_modes_info = None
        # modebb
        self.bb_decay_mode = None
        # ebb1 for mode 4
        self.generated_particles_energy_min = None
        # ebb2
        self.generated_particles_energy_max = None
        # nevents
        self.events_num = None
        # ievstart
        self.first_event_num = None
        # chfile
        self.output_file = None
        self.d['enrange'] = {}
        self.init_data()

    def init_data(self):
        self.process_name = "Double Beta processes."
        self.particle_type = "Xe136"
        self.energy_levels_info = {
            1: "0+ (gs)     {0 MeV}",
            #            1: "2+ (1)      {0.819 MeV}",
            #            2: "2+ (2)      {1.551 MeV}",
            #            3: "0+ (1)      {1.579 MeV}",
            #            4: "2+ (3)      {2.080 MeV}",
            #            5: "2+ (4)      {2.129 MeV}",
            #            6: "0+ (2)      {2.141 MeV}",
            #            7: "2+ (5)      {2.223 MeV}",
            #            8: "0+ (3)      {2.315 MeV}",
            #            9: "2+ (6)      {2.400 MeV}",
        }
        self.energy_level = 0
        self.bb_decay_modes_info = {
            1: '0nubb(mn)         0+ -> 0+     {2n}',
            #            2: '0nubb(rhc-lambda) 0+ -> 0+     {2n}',
            #            3: '0nubb(rhc-lambda) 0+ -> 0+, 2+ {N*}',
            4: '2nubb             0+ -> 0+     {2n}',
            #            5: '0nubbM1           0+ -> 0+     {2n}',
            #            14: '0nubbM2           0+ -> 0+     (2n}',
            #            6: '0nubbM3           0+ -> 0+     {2n}',
            #            13: '0nubbM7           0+ -> 0+     {2n}',
            #            7: '0nubb(rhc-lambda) 0+ -> 2+     {2n}',
            #            8: '2nubb             0+ -> 2+     {2n}, {N*}',
            #            9: '0nuKb+            0+ -> 0+, 2+',
            #            10: '2nuKb+            0+ -> 0+, 2+',
            #            11: '0nu2K             0+ -> 0+, 2+',
            #            12: '2nu2K             0+ -> 0+, 2+',
            #            15: '2nubb             0+ -> 0+ with bosonic neutrinos',
            #            16: '2nubb             0+ -> 2+ with bosonic neutrinos',
            #            17: '0nubb(rhc-eta)    0+ -> 0+ simplified expression',
            #            18: '0nubb(rhc-eta)    0+ -> 0+ with specific NMEs',
        }
        self.bb_decay_mode = 0
        self.generated_particles_energy_min = 0
        self.generated_particles_energy_max = 4.3
        self.events_num = 0
        self.first_event_num = 1

    def get_info(self, energy_level=None, mode=None, energy_min=None, energy_max=None):
        print("Process Name is " + self.process_name)
        print("Process Particle is " + self.particle_type)
        # Load Energy Level
        if not energy_level or energy_level not in self.energy_levels_info.keys():
            print("Please Select one of the following energy level: ")
            for (key, value) in self.energy_levels_info.iteritems():
                print('\t' + str(key) + '\t' + value)
            self.energy_level = input("Your Choice: ")
            if self.energy_level not in self.energy_levels_info.keys():
                print("Wrong Input. Exit.")
                exit(1)
        else:
            self.energy_level = energy_level
        print("Energy Level is " + self.energy_levels_info[self.energy_level])
        # Load Decay Mode
        if not mode or mode not in self.bb_decay_modes_info.keys():
            print("Please Select one of the following decay mode: ")
            for (key, value) in self.bb_decay_modes_info.iteritems():
                print('\t' + str(key) + '\t' + value)
            self.bb_decay_mode = input("Your Choice: ")
            if self.bb_decay_mode not in self.bb_decay_modes_info.keys():
                print("Wrong Input. Exit.")
                exit(1)
        else:
            self.bb_decay_mode = mode
        if self.bb_decay_mode == 4:
            if energy_min == None or energy_max == None:
                print("Do you want to restrict energy range for generated particles?")
                answer = raw_input("Y/N: ")
                if answer == "Y":
                    print("range for sum of e-/e+ energies (MeV): ")
                    self.generated_particles_energy_min = input("Min Energy: ")
                    self.generated_particles_energy_max = input("Max Energy: ")
            else:
                self.generated_particles_energy_min = energy_min
                self.generated_particles_energy_max = energy_max
        self.d['enrange']['ebb1'] = self.generated_particles_energy_min
        self.d['enrange']['ebb2'] = self.generated_particles_energy_max

    def prepare_generate(self):
        # energy release in double beta process: difference
        # between masses of parent and daughter atoms (MeV);
        self.Qbb = 2.468
        # atomic number of daughter nucleus (Z>0 for b-b-
        # and Z<0 for b+b+ and eb+ processes);
        self.Zdbb = 56.
        # mass number of daughter nucleus
        self.Adbb = 136.
        # binding energy of electron on K shell of parent atom (MeV)
        # (for modebb=10 and 11);
        self.EK = 0.
        self.levelE = 0
        self.itrans02 = 0
        self.chdspin = '0+'
        if self.bb_decay_mode == 1:
            self.chmodebb = self.bb_decay_modes_info[self.bb_decay_mode]
        elif self.bb_decay_mode == 4:
            self.chmodebb = self.bb_decay_modes_info[self.bb_decay_mode]
        self.El = self.levelE / 1000.
        self.e0 = self.Qbb
        self.bb(self.bb_decay_mode, self.Qbb, self.levelE / 1000., self.EK, self.Zdbb, self.Adbb, 0)

    def print_info(self):
        print("#    DECAY0 generated file"
              "\n#    Event Type:       " + self.process_name +
              "\n#    Particle:         " + self.particle_type +
              "\n#    Decay Mode:       " + self.chmodebb +
              "\n#    Energy Level:     " + str(self.El) + "MeV"
                                                           "\n")

    # c Function fermi calculates the traditional function of Fermi in
    # c theory of beta decay to take into account the Coulomb correction
    # c to the shape of electron/positron energy spectrum.
    # c Call  : corr=fermi(Z,E)
    # c Input : Z - atomic number of daughter nuclei (>0 for e-, <0 for e+);
    # c         E - kinetic energy of particle (MeV; E>50 eV).
    # c Output: corr - value of correction factor (without normalization -
    # c                constant factors are removed - for MC simulation).
    # c V.I.Tretyak, 15.07.1992.

    @staticmethod
    def fermi(Z, E):
        if E < 50e-6:
            E = 50e-6
        alfaz = Z / 137.036
        w = E / 0.511 + 1.
        p = math.sqrt(w * w - 1.)
        y = alfaz * w / p
        g = math.sqrt(1. - alfaz ** 2)
        carg = complex(g, y)
        return p ** (2. * g - 2.) * math.exp(3.1415927 * y + 2. * math.log(abs(function.gamma(carg))))

    # probability distribution for energy of first e-/e+ for modebb=1
    @staticmethod
    def fe1_mod1(e1, Zdbb, Adbb, e0):
        if e1 > e0:
            return 0
        e2 = e0 - e1
        p1 = math.sqrt(e1 * (e1 + 2. * emass))
        p2 = math.sqrt(e2 * (e2 + 2. * emass))
        return (e1 + emass) * p1 * Generate.fermi(Zdbb, e1) * (e2 + emass) * p2 * Generate.fermi(Zdbb, e2)

    @staticmethod
    def fe12_mod4(e2, Zdbb, Adbb, e0, e1):
        if e2 > (e0 - e1):
            return 0
        p1 = math.sqrt(e1 * (e1 + 2. * emass))
        p2 = math.sqrt(e2 * (e2 + 2. * emass))
        return (e1 + emass) * p1 * Generate.fermi(Zdbb, e1) * (e2 + emass) * p2 * Generate.fermi(Zdbb, e2) * \
               (e0 - e1 - e2) ** 5

    @staticmethod
    def dshelp(y, x, Zdbb, Adbb, e0):
        if x > 0 and y > 0 and x + y < e0:
            return generate.fe12_mod4(y, Zdbb, Adbb, e0, x)
        return 0

    @staticmethod
    def dshelp_min(x):
        return max(0, dshelp_dens - x)

    @staticmethod
    def dshellp_max(x):
        return dshelp_denf - x

    # sampling the energies and angles of electrons in various modes
    # of double beta decay without Primakoff-Rosen approximation.
    def bb(self, modebb, Qbb, Edlevel, EK, Zdbb, Adbb, istartbb):

        # Define Parameters
        precision = 0
        dens = 0
        denf = 0
        chhelp = ""
        chfile = ""
        spthe1 = {}
        spthe2 = []
        # Load Parameters
        # tevst = self.d['genevent']['tevst']
        # npfull = self.d['genevent']['npfull']
        # npgeant = self.d['genevent']['npgeant']
        # pmoment = self.d['genevent']['pmoment']
        # ptime = self.d['genevent']['ptime']

        ebb1 = self.d['enrange']['ebb1']
        ebb2 = self.d['enrange']['ebb2']
        # toallevents = self.d['enrange']['toallevents']
        # lhelp = self.d['enrange']['lhep']
        # chhelp = self.d['enerange']['chhelp']
        #
        # dens = self.d['denrange']['dens']
        # denf = self.d['denrange']['denf']
        # mode = self.d['denrange']['mode']

        # Zd = self.d['helpbb']['Zd']
        # Ad = self.d['helpbb']['Ad']
        # e0 = self.d['helpbb']['e0']
        # e1 = self.d['helpbb']['e1']

        # chi_GTw = self.d['eta_name']['chi_GTw']
        # chi_Fw = self.d['eta_name']['chi_Fw']
        # chip_GT = self.d['eta_name']['chip_GT']
        # chip_F = self.d['eta_name']['chip_F']
        # chip_T = self.d['eta_name']['chip_T']
        # chip_P = self.d['eta_name']['chip_P']
        # chip_R = self.d['eta_name']['chip_R']

        # Start Caculate
        two_pi = 2. * pi
        Zd = Zdbb
        Ad = Adbb
        e0 = Qbb - Edlevel
        if istartbb == 0:
            if self.generated_particles_energy_min < 0:
                self.generated_particles_energy_min = 0
            if self.generated_particles_energy_max > e0:
                self.generated_particles_energy_max = e0
            spmax = -1
            b2amin = 1e20
            b2amax = -1e20
            relerr = 1e-4
            for i in range(1, int(math.ceil(e0 * 1000))):
                e1 = i / 1000.
                e1h = e1
                spthe1[i] = 0
                if modebb == 1:
                    spthe1[i] = generate.fe1_mod1(e1h, Zdbb, Adbb, e0)
                elow = max(1.e-4, ebb1 - e1 + 1.e-4)
                ehigh = max(1.e-4, ebb2 - e1 + 1.e-4)
                if modebb == 4:
                    spthe1[i] = integrate.quad(Generate.fe12_mod4, elow, ehigh, (Zdbb, Adbb, e0, e1))[0]
                if spthe1[i] > spmax:
                    spmax = spthe1[i]
            for i in range(int(math.ceil(e0 * 1000)), 4301):
                spthe1[i] = 0
            toallevents = 1
            if modebb == 4:
                mode = modebb
                dens = 0
                denf = e0
                dshelp_dens = dens
                dshelp_denf = denf
                r1 = integrate.dblquad(Generate.dshelp, 0, denf, Generate.dshelp_min, Generate.dshellp_max,
                                       args=(Zdbb, Adbb, e0))
                print r1


if __name__ == '__main__':
    generate = Generate()
    generate.init_data()
    generate.get_info(energy_level=1, mode=4, energy_min=0, energy_max=4.3)
    generate.prepare_generate()
    generate.print_info()

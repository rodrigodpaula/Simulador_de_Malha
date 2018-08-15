from datetime import datetime, timedelta
import os.path

class Simulator:

    def __init__(self, network, btgen):
        self.network = network
        self.btgen = btgen
        self.legs = []

    def clear(self):
        for leg in self.legs:
            leg.adt = None
            leg.aat = None
            leg.block = None
            leg.delay_reason = None
        self.legs = []

    def output(self, file_name):
        self.__write_header__(file_name)
        with open(file_name, 'a') as f:
            for number in sorted(map(int, self.network.routes)):
                for leg in self.network.routes[str(number)].legs:
                    if leg.delay_reason:
                        f.write(self.__output_string__(leg))

    def __write_header__(self, file_name):
        if not os.path.isfile(file_name):
            with open(file_name, 'w') as f:
                h = 'TRILHO;FROTA;NUM;DE;PARA;SDT;SAT;BL PL;ADT;AAT;BL EX;STATUS;DEP DL;ARR DL;CNX PL;CNX PR;CNX EX;' \
                         'CR TRILHO;CR FROTA;CR NUM;CR DE;CR PARA;CR SDT;CR SAT;CR ADT;CR AAT\n'
                f.write(h)

    def __output_string__(self, leg):
        sdtstr = leg.sdt.strftime('%d/%m/%y %H:%M:%S')
        satstr = leg.sat.strftime('%d/%m/%y %H:%M:%S')
        adtstr = leg.adt.strftime('%d/%m/%y %H:%M:%S')
        aatstr = leg.aat.strftime('%d/%m/%y %H:%M:%S')
        block_m = (leg.sat - leg.sdt).total_seconds() / 60
        plan_block = '%02d:%02d' % (int(block_m / 60), block_m % 60)
        exec_block = '%02d:%02d' % (int(leg.block / 60), leg.block % 60)
        dep_delay = (leg.adt - leg.sdt).total_seconds() / 60
        arr_delay = (leg.aat - leg.sat).total_seconds() / 60
        next = leg.next
        plan_cnx = int((next.sdt - leg.sat).total_seconds() / 60) if next and next.sdt else ''
        proj_cnx = int((next.sdt - leg.aat).total_seconds() / 60) if next and next.adt else ''
        exec_cnx = int((next.adt - leg.aat).total_seconds() / 60) if next and next.adt else ''
        output = '%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%d;%d;%s;%s;%s' % (
            leg.route.number,
            str(leg.route.fleet),
            leg.number.strip(),
            leg.fr.code,
            leg.to.code,
            sdtstr,
            satstr,
            plan_block,
            adtstr,
            aatstr,
            exec_block,
            leg.delay_reason,
            dep_delay,
            arr_delay,
            plan_cnx,
            proj_cnx,
            exec_cnx
        )
        return output + ';%s;%s;%s;%s;%s;%s;%s;%s;%s\n' % (
            leg.last_crew_leg.route.number,
            str(leg.last_crew_leg.route.fleet),
            leg.last_crew_leg.number.strip(),
            leg.last_crew_leg.fr.code,
            leg.last_crew_leg.to.code,
            leg.last_crew_leg.sdt.strftime('%d/%m/%y %H:%M:%S'),
            leg.last_crew_leg.sat.strftime('%d/%m/%y %H:%M:%S'),
            leg.last_crew_leg.adt.strftime('%d/%m/%y %H:%M:%S'),
            leg.last_crew_leg.aat.strftime('%d/%m/%y %H:%M:%S')
        ) if leg.last_crew_leg else output + '\n'

    def simulate(self, begin, end):
        self.__filter_and_sort_legs__(begin, end)
        for leg in self.legs:
            aircraft_time = self.__get_aircraft_time__(leg)
            crew_time = self.__get_crew_time__(leg)
            max_time = self.__get_max_time__(aircraft_time, crew_time)
            if max_time and max_time > leg.sdt:
                leg.adt = max_time
                leg.delay_reason = 'TR' if max_time == aircraft_time else 'CR'
            else:
                leg.adt = leg.sdt
                leg.delay_reason = 'OK'
            self.__set_block_time__(leg)
            leg.aat = leg.adt + timedelta(minutes=leg.block)

    def __filter_and_sort_legs__(self, begin, end):
        self.legs = filter(lambda x: begin <= x.sdt <= end, self.network.legs.values())
        self.legs = sorted(self.legs, key=lambda leg: leg.sdt)

    def __set_block_time__(self, leg):
        block_h = self.btgen.get_block(leg.fr.code, leg.to.code)
        block_m = round(60 * block_h, 0) if block_h else None
        leg.block = block_m if block_m else (leg.sat - leg.sdt).seconds / 60

    def __get_max_time__(self, aircraft_time, crew_time):
        if aircraft_time and crew_time:
            return max(aircraft_time, crew_time)
        elif aircraft_time:
            return aircraft_time
        elif crew_time:
            return crew_time
        return None

    def __get_aircraft_time__(self, leg):
        if leg.prev and leg.prev.aat:
            turn_around = self.__get_aircraft_turn_around__(leg.fr, leg.route.fleet)
            return leg.prev.aat + timedelta(minutes=turn_around)
        return None

    # crew_complement = [1, 1, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0]
    # self.crew_from_legs[pos] = [leg, ..., leg]
    def __get_crew_time__(self, leg):
        times = {}
        for pos in leg.crew_from_legs:
            # Only CP position
            # if pos == 0:
            for from_leg in leg.crew_from_legs[pos]:
                if from_leg and from_leg.aat and from_leg not in times:
                    ac_change = (from_leg.route.number != leg.route.number)
                    connection = self.__get_crew_min_connection__(leg.fr) if ac_change else \
                                 self.__get_aircraft_turn_around__(leg.fr, leg.route.fleet)
                    times[from_leg] = from_leg.aat + timedelta(minutes=connection)
        leg.last_crew_leg = max(times, key=times.get) if len(times) > 0 else None
        return max(times.values()) if len(times) > 0 else None

    def __get_aircraft_turn_around__(self, airport, fleet):
        if fleet.main == 'B73G':
            return 30
        else:
            if airport.code in ['CGH']:
                return 30
            elif airport.code in ['GRU', 'GIG', 'BSB', 'EZE']:
                return 40
            else:
                return 30

    def __get_crew_min_connection__(self, airport):
        if airport.code in ['CGH', 'GRU', 'GIG', 'BSB']:
            return 0
        else:
            return 0

from netsim.objects import Airport, Fleet, Leg, Route


class Network:

    def __init__(self):
        self.airports = {}
        self.fleets = {}
        self.routes = {}
        self.legs = {}
        self.__add_known_fleets__()

    def __add_known_fleets__(self):
        self.fleets[('B738', '738')] = Fleet(main='B738', sub='738')
        self.fleets[('B738', '73A')] = Fleet(main='B738', sub='73A')
        self.fleets[('B738', '73M')] = Fleet(main='B738', sub='73M')
        self.fleets[('B73H', '73H')] = Fleet(main='B73H', sub='73H')
        self.fleets[('B738', '7M8')] = Fleet(main='B738', sub='7M8')
        self.fleets[('B73G', '73G')] = Fleet(main='B73G', sub='73G')

    def add(self, flight_number, fr, to, sdt, sat, main, sub, route_number):
        key = (flight_number, sdt)
        if key not in self.legs:
            if fr not in self.airports:
                self.airports[fr] = Airport(fr)
            if to not in self.airports:
                self.airports[to] = Airport(to)
            if route_number not in self.routes:
                self.routes[route_number] = Route(route_number, self.fleets[(main, sub)])
            frapt = self.airports[fr]
            toapt = self.airports[to]
            route = self.routes[route_number]
            leg = Leg(flight_number, frapt, toapt, sdt, sat, route)
            self.legs[key] = leg
            route.add(leg)

    def sort_routes(self):
        for route in self.routes.values():
            route.sort()

    def print_legs(self):
        for leg in self.legs.values():
            print '%s' % str(leg)
            print '  PREV: %s' % str(leg.prev)
            print '  NEXT: %s' % str(leg.next)

    def print_crew_flow(self):
        for leg in self.legs.values():
            print '%s' % str(leg)
            for p in leg.crew_from_legs:
                from_legs = leg.crew_from_legs[p]
                print '  POSITION %02d [%d]:' % (p, len(from_legs))
                for leg_from in from_legs:
                    print '    %s' % str(leg_from)

    def __str__(self):
        sb = []
        for number in sorted(map(int, self.routes)):
            key = str(number)
            sb.append(str(self.routes[key]))
        return '\n'.join(sb)
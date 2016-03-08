#!/usr/bin/python2
import re
import subprocess
import os
import uuid
import argparse
import sys
import string


class Convert:
    class Comment:
        def __init__(self, str):
            self.comment = str

    class Event:
        def __init__(self):
            self.particles = []

        def __len__(self):
            return len(self.particles)

    class Particle:
        def __init__(self):
            self.PDGCode = 0
            # in GeV
            self.momentum = []
            # in ns
            self.time = 0

    def __init__(self):
        self.file = None
        self.file_lines = []
        self.data_lines = []
        self.output = None
        pass

    def load_from_file(self, input_file):
        self.file = open(input_file, "r")
        for line in self.file:
            self.file_lines.append(line)
        self.file.close()

    def parse(self):
        event = self.Event()
        for line in self.file_lines:
            if re.match("^\s*\d*\s*0\.00000\s*2\n$", line):
                if len(event) > 0:
                    self.data_lines.append(event)
                event = self.Event()
            elif re.match(
                    "^\s*\d*\s*-?\d*\.\d*E?-?\d{0,2}\s*-?\d*\.\d*E?-?\d{0,2}\s*-?\d*\.\d*E?-?\d{0,2}\s*0\.00000\s*\n$",
                    line):
                particle = self.Particle()
                line.strip()
                data = line.split()
                particle.PDGCode = 11
                particle.momentum = [data[1], data[2], data[3]]
                particle.time = data[4]
                event.particles.append(particle)
            else:
                self.data_lines.append(self.Comment(line))

    def save_to_file(self):
        if self.output:
            self.output = open(unicode(self.output), "w")
        else:
            self.output = sys.stdout
        event_count = 0
        for line in self.data_lines:
            if isinstance(line, self.Comment):
                pass
            elif isinstance(line, self.Event):
                event_count += 1
                self.output.write(str(event_count) + " " + str(len(line)) + "\n")
                particle_count = 0
                for particle in line.particles:
                    particle_count += 1
                    self.output.write("%s %s %s %s %s\n" %
                                      (particle_count, particle.PDGCode, float(particle.momentum[0]) / 1000,
                                       float(particle.momentum[1]) / 1000,
                                       float(particle.momentum[2]) / 1000))
        self.output.flush()
        self.output.close()


class Manager():
    def __init__(self):
        self.convert = Convert()
        self.program_handler = None
        self.inputs = []
        self.program_name = './decay0'
        self.tmp_file = uuid.uuid4().__str__() + ".tmp"
        self.output_file = None

    def parse(self, input, num):
        if input == "0nubb":
            self.inputs = ['1', 'Xe136', '0', '1', str(num), '1']
        else:
            self.inputs = ["1", "Xe136", "0", "4", "N", str(num), "1"]

    def run(self):
        if not os.path.isfile(self.program_name):
            print("Decay0 didn't find. Please put it in the same directory.")
        self.program_handler = subprocess.Popen(self.program_name,
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
        for input in self.inputs:
            self.program_handler.stdin.write(input + "\n")
        self.program_handler.stdin.write("y\n")
        self.program_handler.stdin.write(self.tmp_file + "\n")
        self.program_handler.communicate()
        self.program_handler.wait()
        self.convert.load_from_file(self.tmp_file)
        self.convert.parse()
        self.convert.output = self.output_file
        self.convert.save_to_file()
        os.remove(self.tmp_file)


def build_arg_parser():
    parser = argparse.ArgumentParser(description='Wrapper of Decay0.')
    # parser.add_argument('-c', '--config', help="The Info passed to Decay0. Like 1|Xe136|0|1|1000|1", required=True)
    parser.add_argument('-m', '--mode', choices=["0nubb", "2nubb"], required=True,
                        help="Input the mode of Double Beta Decay.")
    parser.add_argument('-n', '--num', type=int, default=100, help="The number of generated events.")
    parser.add_argument('-o', '--output', help="Output file.")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    return parser


if __name__ == '__main__':
    args = build_arg_parser().parse_args()
    manager = Manager()
    manager.parse(args.mode, args.num + 1)
    if args.output:
        manager.output_file = args.output
    manager.run()

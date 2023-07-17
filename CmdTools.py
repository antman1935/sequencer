# author: antman1935, anthony.lamont99@yahoo.com

from Restrictions import Restriction
    
class CommandOptions:
    def getParameters(self):
        raise Exception("unimplemented")

"""
Base class for all of the commands we'll create. Has a generator function that should
be overriden by all the subclasses.
"""
class Command:
    commands = {}
    def internal_generator(self):
        raise Exception("unimplemented")
    
    def generator(self):
        for element in self.internal_generator():
            if self.checkRestrictions(element):
                yield element
    
    def flat_generator(self):
        return None
    
    def __str__(self):
        raise Exception("unimplemented")
    
    def setRestrictions(self, res: list[list[Restriction]]):
        self.restrictions = res

    def checkRestrictions(self, element):
        if self.restrictions is None or len(self.restrictions) == 0:
            return True
        cache = {}
        for restr_set in self.restrictions:
            all = [restriction.passes(element, cache) for restriction in restr_set]
            if sum(all) == len(all):
                return True
        return False
    
    def register(commandClass):
        assert not commandClass.name in Command.commands, f"The name {commandClass.name} is already associated with the command {Command.commands[commandClass.name]}. Registering {commandClass} failed."
        Command.commands[commandClass.name] = commandClass

    """
    Convienence function for testing generator output. Given a command that generates words, check that
    its output matches the list. Gives delta from both list if there is a miss-match.
    """
    def generator_test(name: str, generator, expected_list):
        print(name)
        cmd_m_expected_list = []
        expected_list_m_cmd = []

        temp = []
        for word in generator:
            if not word in expected_list:
                cmd_m_expected_list.append(word)
            else:
                temp.append(word)

        for word in expected_list:
            if not word in temp:
                expected_list_m_cmd.append(word)

        if len(cmd_m_expected_list) > 0 or len(expected_list_m_cmd) > 0:
            print(f"Generator test failed.\n\tExtra entries generated: {cmd_m_expected_list}.\n\tExpected entries missed: {expected_list_m_cmd}.")
            return False
    
        print("Success!")
        return True

Command.register = staticmethod(Command.register)
Command.generator_test = staticmethod(Command.generator_test)

from Importer import Importer

Importer.importSubdirectory("Commands")
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# written by: Jeff Ortel ( jortel@redhat.com )

import sys
sys.path.append('../')

from suds import *
from suds.serviceproxy import ServiceProxy
from suds.schema import Schema
from suds.sudsobject import Object
from suds.wsdl import WSDL
from suds.bindings.binding import Binding
from suds.bindings.literal.marshaller import Marshaller
from suds.bindings.encoded.marshaller import Marshaller as Encoder
from suds.bindings.unmarshaller import Unmarshaller
from suds.sax import Parser


urlfmt = 'http://localhost:7080/rhq-rhq-enterprise-server-ejb3/%s?wsdl'

services = \
{ 
    'test':'WebServiceTestBean', 
    'rpc':'RPCEncodedBean', 
    'auth':'SubjectManagerBean', 
    'resources':'ResourceManagerBean', 
    'perspectives':'PerspectiveManagerBean', 
    'content':'ContentManagerBean', 
    'contentsource':'ContentSourceManagerBean'
}

def get_url(name):
    return urlfmt % services[name]

class Test:
    
    def test_misc(self):
        
        service = ServiceProxy('file:///home/jortel/Desktop/misc/suds_files/WebServiceTestBean.wsdl.xml')
        print service
        #print service.__client__.schema
        print service.get_instance('person')
        print service.get_instance('person.jeff')
        
        service = ServiceProxy('http://soa.ebrev.info/service.wsdl')
        print service
        
        service = ServiceProxy('https://sec.neurofuzz-software.com/paos/genSSHA-SOAP.php?wsdl')
        print service
        print service.genSSHA('hello', 'sha1')
        
        service = ServiceProxy('http://www.services.coxnewsweb.com/COXnetUR/URService?WSDL')
        print service
        try:
            bean = service.getUserBean('abc', '123', 'mypassword', 'myusername')
        except WebFault, f:
            print f
            
        return
        
        service = ServiceProxy(get_url('test'))
        
        marshaller = Marshaller(service.binding)
        encoder = Encoder(service.binding)
        unmarshaller = Unmarshaller(service.binding)
        
        p = service.get_instance('person')
        p.name.first='jeff'
        p.name.last='ortel'
        p.age = 21
        ph = service.get_instance('phone')
        ph.nxx = 919
        ph.npa = 606
        ph.number = None
        p.phone.append(ph)
        print p
        print encoder.process('person', p)
        sys.exit()
        
        x = """
        <person xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <name>
                <first>jeff</first>
                <middle/>
                <last xsi:nil="true"/>
            </name>
        </person>
        """
        node = Parser().parse(string=x).root()
        service.binding.nil_supported = True
        p = unmarshaller.process(node)
        print p
        service.binding.nil_supported = False
        p = unmarshaller.process(node)
        print p
        service.binding.nil_supported = True
        print marshaller.process('dog', p)
        service.binding.nil_supported = False
        print marshaller.process('dog', p)

        p = Object()
        p2 = Object()
        p2.msg='hello'
        p2.xx =10
        p.name = ['jeff', p2]
        print p

        p = Object()
        p.first = u'jeff'+unichr(1234)
        p.age = u'44'
        x = str(p)

        p = unmarshaller.process(Parser().parse(file='/home/jortel/Desktop/x.xml'))
        print p
    
    def basic_test(self):
        
        #
        # create a service proxy using the wsdl.
        #
        service = ServiceProxy(get_url('test'))
        
        #
        # print the service (introspection)
        #
        print service
        
        #
        # create a name object using the wsdl
        #
        name = service.get_instance('tns:name')
        name.first = u'jeff'+unichr(1234)
        name.middle = None
        name.last = 'ortel'
        
        #
        # create a phone object using the wsdl
        #
        phoneA = service.get_instance('phone')
        phoneA.npa = 410
        phoneA.nxx = 822
        phoneA.number = 5138

        phoneB = service.get_instance('phone')
        phoneB.npa = 919
        phoneB.nxx = 606
        phoneB.number = 4406
        
        #
        # create a person object using the wsdl
        #
        person = service.get_instance('person')
        
        #
        # inspect empty person
        #
        print '{empty} person=\n%s' % person
        
        person.name = name
        person.age = 43
        person.phone.append(phoneA)
        #person.phone.append(phoneB)
        
        #
        # inspect person
        #
        print 'person=\n%s' % person
        
        #
        # add the person (using the webservice)
        #
        print 'addPersion()'
        result = service.addPerson(person)
        print '\nreply(\n%s\n)\n' % result.encode('utf-8')
        
        #
        # create a new name object used to update the person
        #
        newname = service.get_instance('name')
        newname.first = 'Todd'
        newname.last = None
        
        #
        # update the person's name (using the webservice) and print return person object
        #
        print 'updatePersion()'
        result = service.updatePerson(person, newname)
        print '\nreply(\n%s\n)\n' % str(result)
        result = service.updatePerson(person, None)
        print '\nreply(\n%s\n)\n' % str(result)
        
        
        #
        # invoke the echo service
        #
        print 'echo()'
        result = service.echo('this is cool')
        print '\nreply( %s )\n' % str(result)
        
        #
        # invoke the hello service
        #
        print 'hello()'
        result = service.hello()
        print '\nreply( %s )\n' % str(result)
        
        #
        # invoke the testVoid service
        #
        try:
            print 'testVoid()'
            result = service.testVoid()
            print '\nreply( %s )\n' % str(result)
        except Exception, e:
            print e

        #
        # test list args
        #
        print 'testListArgs(list)'
        mylist = ['my', 'dog', 'likes', 'steak']
        result = service.testListArg(mylist)
        print '\nreply( %s )\n' % str(result)
        # tuple
        print 'testListArgs(tuple)'
        mylist = ('my', 'dog', 'likes', 'steak')
        result = service.testListArg(mylist)
        print '\nreply( %s )\n' % str(result)
        
        #
        # test list returned
        #
        print 'getList(str, 1)'
        result = service.getList('hello', 1)
        print '\nreply( %s )\n' % str(result)
        
        print 'getList(str, 3)'
        result = service.getList('hello', 3)
        print '\nreply( %s )\n' % str(result)
        
        #
        # test exceptions
        #
        try:
            print 'testExceptions()'
            result = service.testExceptions()
            print '\nreply( %s )\n' % tostr(result)
        except Exception, e:
            print e
            
    def rpc_test(self):
        
        #
        # create a service proxy using the wsdl.
        #
        service = ServiceProxy(get_url('rpc'))
        
        #
        # print the service (introspection)
        #
        print service
        
        #
        # create a name object using the wsdl
        #
        name = service.get_instance('tns:name')
        name.first = 'jeff'
        name.last = 'ortel'
        
        #
        # create a phone object using the wsdl
        #
        phoneA = service.get_instance('phone')
        phoneA.npa = 410
        phoneA.nxx = 822
        phoneA.number = 5138

        phoneB = service.get_instance('phone')
        phoneB.npa = 919
        phoneB.nxx = 606
        phoneB.number = 4406
        
        #
        # create a person object using the wsdl
        #
        person = service.get_instance('person')
        
        #
        # inspect empty person
        #
        print '{empty} person=\n%s' % person
        
        person.name = name
        person.age = 43
        person.phone.append(phoneA)
        person.phone.append(phoneB)
        
        #
        # inspect person
        #
        print 'person=\n%s' % person
        
        #
        # add the person (using the webservice)
        #
        print 'addPersion()'
        result = service.addPerson(person)
        print '\nreply(\n%s\n)\n' % str(result)
        
        #
        # create a new name object used to update the person
        #
        newname = service.get_instance('name')
        newname.first = 'Todd'
        newname.last = 'Sanders'
        
        #
        # update the person's name (using the webservice) and print return person object
        #
        print 'updatePersion()'
        result = service.updatePerson(person, newname)
        print '\nreply(\n%s\n)\n' % str(result)
        print 'updatePersion() newperson = None'
        result = service.updatePerson(person, None)
        print '\nreply(\n%s\n)\n' % str(result)
        
        #
        # invoke the echo service
        #
        print 'echo()'
        result = service.echo('this is cool')
        print '\nreply( %s )\n' % str(result)
        
        #
        # invoke the hello service
        #
        print 'hello()'
        result = service.hello()
        print '\nreply( %s )\n' % str(result)
        
        #
        # invoke the testVoid service
        #
        try:
            print 'testVoid()'
            result = service.testVoid()
            print '\nreply( %s )\n' % str(result)
        except Exception, e:
            print e
        
        #
        # test exceptions
        #
        try:
            print 'testExceptions()'
            result = service.testExceptions()
            print '\nreply( %s )\n' % str(result)
        except Exception, e:
            print e

    def rpc_enctest(self):
        

        try:
            service = ServiceProxy('http://test.closingmarket.com/ClosingMarketService/cminterface.asmx?WSDL')
            print service
            token = service.Login( 'DVTest1@bbwcdf.com', 'DevTest1')
            print token
        except Exception, e:
            print e
            
        print '************ JEFF ***************'
        
        #
        # create a service proxy using the wsdl.
        #
        service = ServiceProxy('http://127.0.0.1:8080/axis/services/Jeff?wsdl')
        
        #
        # print the service (introspection)
        #
        print service
        
        #
        # create a person object using the wsdl
        #
        person = service.get_instance('Person')
        
        #
        # inspect empty person
        #
        print '{empty} person=\n%s' % person
        
        person.name = 'jeff ortel'
        person.age = 43
        
        #
        # inspect person
        #
        print 'person=\n%s' % person
        
        #
        # add the person (using the webservice)
        #
        print 'addPersion()'
        result = service.addPerson(person)
        print '\nreply(\n%s\n)\n' % str(result)


    def auth_test(self):
        
        service = ServiceProxy(get_url('auth'))
        
        #
        # print the service (introspection)
        #
        print service
            
        #
        # login
        #
        print 'login()'
        subject = service.login('rhqadmin', 'rhqadmin')
        print '\nreply(\n%s\n)\n' % str(subject)
        
        #
        # create page control and get all subjects
        #
        pc = service.get_instance('pageControl')
        pc.pageNumber = 0
        pc.pageSize = 0
        
        print 'getAllSubjects()'
        users = service.getAllSubjects(pc)
        print 'Reply:\n(\n%s\n)\n' % str(users)
        
        #
        # get user preferences
        #
        print 'loadUserConfiguration()'
        id = subject.id
        print subject
        prefs = service.loadUserConfiguration(id)
        print 'Reply:\n(\n%s\n)\n' % str(prefs)
        

    def resource_test(self):
        
        print 'testing resources (service) ...'
        
        #
        # create a service proxy using the wsdl.
        #
        service = ServiceProxy(get_url('resources'))

        #
        # print the service (introspection)
        #
        print service

        #
        # login
        #
        print 'login()'
        subject = ServiceProxy(get_url('auth')).login('rhqadmin', 'rhqadmin')
        
        #
        # create page control and get all subjects
        #
        pc = service.get_instance('pageControl')
        pc.pageNumber = 0
        pc.pageSize = 0
        
        #
        # get enumerations
        #
        resourceCategory = service.get_enum('resourceCategory')
        print 'Enumeration (resourceCategory):\n%s' % resourceCategory
        
        
        #
        # get resource by category
        #
        print 'getResourcesByCategory()'
        platforms = service.getResourcesByCategory(subject, resourceCategory.PLATFORM, 'COMMITTED', pc)
        print 'Reply:\n(\n%s\n)\n' % str(platforms)
        
        #
        # get resource tree
        #
        for p in platforms:
            print 'getResourcesTree()'
            tree = service.getResourceTree(p.id)
            print 'Reply:\n(\n%s\n)\n' % str(tree)
            
    def perspectives_test(self):
        
        print 'testing perspectives (service) ...'
        
        #
        # create a service proxy using the wsdl.
        #
        url = get_url('perspectives')
        print url
        service = ServiceProxy(url)
        
        gtr = service.get_instance('getTasksResponse.return')
        print gtr

        #
        # print the service (introspection)
        #
        print service

        #
        # login
        #
        print 'login()'
        auth = ServiceProxy(get_url('auth'))
        print auth
        subject = auth.login('rhqadmin', 'rhqadmin')

        #
        # get all perspectives
        #
        print 'getPerspective()'
        perspectives = service.getPerspective("content")
        print 'perspectives: ', str(perspectives)
        
        print 'getAllPerspective()'
        perspectives = service.getAllPerspectives()
        print 'perspectives: ', str(perspectives)
        
    def contentsource_test(self):
        
        print 'testing content source (service) ...'
        
        #
        # create a service proxy using the wsdl.
        #
        service = ServiceProxy(get_url('contentsource'))

        #
        # print the service (introspection)
        #
        print service
        print service.__client__.schema
        
        configuration = service.get_instance('configuration')
        entry = service.get_instance('configuration.tns:properties.entry')
        simple = service.get_instance('propertySimple')
        entry.key = 'location'
        simple.name = 'location'
        simple.stringValue = 'http://download.skype.com/linux/repos/fedora/updates/i586'
        entry.value = simple
        configuration.properties.entry.append(entry)
        configuration.notes = 'SkipeAdapter'
        configuration.version = 1234
        print configuration
        
        name = 'SkipeAdapter'
        description = 'The skipe adapter'
        type = 'YumSource'

        #
        # login
        #
        print 'login()'
        subject = ServiceProxy(get_url('auth')).login('rhqadmin', 'rhqadmin')

        #
        # get all perspectives
        #
        try:
            print 'createContentSource()'
            result = service.createContentSource(subject, name, description, type, configuration, False)
            print 'createContentSource: ', str(result)
        except Exception, e:
            print e

if __name__ == '__main__':
    
    #logger('serviceproxy').setLevel(logging.DEBUG)
    test = Test()
    test.test_misc()
    test.basic_test()
    test.rpc_test()
    test.rpc_enctest()
    test.auth_test()
    test.resource_test()
    test.perspectives_test()
    test.contentsource_test()

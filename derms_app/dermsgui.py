# -------------------------------------------------------------------------------
# Copyright (c) 2019, Battelle Memorial Institute All rights reserved.
# Battelle Memorial Institute (hereinafter Battelle) hereby grants permission to any person or entity
# lawfully obtaining a copy of this software and associated documentation files (hereinafter the
# Software) to redistribute and use the Software in source and binary forms, with or without modification.
# Such person or entity may use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and may permit others to do so, subject to the following conditions:
# Redistributions of source code must retain the above copyright notice, this list of conditions and the
# following disclaimers.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
# the following disclaimer in the documentation and/or other materials provided with the distribution.
# Other than as used herein, neither the name Battelle Memorial Institute or Battelle may be used in any
# form whatsoever without the express written consent of Battelle.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# BATTELLE OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# General disclaimer for use with OSS licenses
#
# This material was prepared as an account of work sponsored by an agency of the United States Government.
# Neither the United States Government nor the United States Department of Energy, nor Battelle, nor any
# of their employees, nor any jurisdiction or organization that has cooperated in the development of these
# materials, makes any warranty, express or implied, or assumes any legal liability or responsibility for
# the accuracy, completeness, or usefulness or any information, apparatus, product, software, or process
# disclosed, or represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer,
# or otherwise does not necessarily constitute or imply its endorsement, recommendation, or favoring by the United
# States Government or any agency thereof, or Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by BATTELLE for the
# UNITED STATES DEPARTMENT OF ENERGY under Contract DE-AC05-76RL01830
# -------------------------------------------------------------------------------
"""
Created on Sep 15, 2019

@author: Craig Allwardt
"""

__version__ = "0.0.1"

from SPARQLWrapper import SPARQLWrapper2
from derms_app import constants
from derms_app import derms_group as grp

sparql = SPARQLWrapper2(constants.blazegraph_url)

# selecting from all feeders in the database; we can group across feeders
#fidselect = """ VALUES ?fdrid {\"""" + sys.argv[1] + """\"}
fidselect = """ 
 ?s c:Equipment.EquipmentContainer ?fdr.
 ?fdr c:IdentifiedObject.mRID ?fdrid. """

qstrSolar = constants.prefix + """SELECT ?name ?uname ?bus ?ratedS ?ratedU ?p ?q (group_concat(distinct ?phs;separator=\"\") as ?phases) ?eqid ?fdrid WHERE {
	SELECT ?name ?uname ?bus ?ratedS ?ratedU ?p ?q ?eqid ?fdrid ?phs WHERE {""" + fidselect + """
 ?s r:type c:PowerElectronicsConnection.
 ?s c:IdentifiedObject.name ?name.
 ?s c:IdentifiedObject.mRID ?eqid. 
 ?peu r:type c:PhotovoltaicUnit.
 ?peu c:IdentifiedObject.name ?uname.
 ?s c:PowerElectronicsConnection.PowerElectronicsUnit ?peu.
 ?s c:PowerElectronicsConnection.ratedS ?ratedS.
 ?s c:PowerElectronicsConnection.ratedU ?ratedU.
 ?s c:PowerElectronicsConnection.p ?p.
 ?s c:PowerElectronicsConnection.q ?q.
 ?t c:Terminal.ConductingEquipment ?s.
 ?t c:Terminal.ConnectivityNode ?cn. 
 ?cn c:IdentifiedObject.name ?bus.
 OPTIONAL {?pep c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?s.
 ?pep c:PowerElectronicsConnectionPhase.phase ?phsraw.
	bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) } } ORDER BY ?name ?phs
 } GROUP BY ?name ?uname ?bus ?ratedS ?ratedU ?p ?q ?eqid ?fdrid
 ORDER BY ?name
"""

qstrStorage = constants.prefix + """SELECT ?name ?uname ?bus ?ratedS ?ratedU ?ratedE ?storedE ?p ?q (group_concat(distinct ?phs;separator=\"\") as ?phases) ?eqid ?fdrid WHERE {
	SELECT ?name ?uname ?bus ?ratedS ?ratedU ?ratedE ?storedE ?p ?q ?eqid ?fdrid ?phs WHERE {""" + fidselect + """
 ?s r:type c:PowerElectronicsConnection.
 ?s c:IdentifiedObject.name ?name.
 ?s c:IdentifiedObject.mRID ?eqid. 
 ?peu r:type c:BatteryUnit.
 ?peu c:IdentifiedObject.name ?uname.
 ?s c:PowerElectronicsConnection.PowerElectronicsUnit ?peu.
 ?s c:PowerElectronicsConnection.ratedS ?ratedS.
 ?s c:PowerElectronicsConnection.ratedU ?ratedU.
 ?s c:PowerElectronicsConnection.p ?p.
 ?s c:PowerElectronicsConnection.q ?q.
 ?peu c:BatteryUnit.ratedE ?ratedE.
 ?peu c:BatteryUnit.storedE ?storedE.
 ?t c:Terminal.ConductingEquipment ?s.
 ?t c:Terminal.ConnectivityNode ?cn. 
 ?cn c:IdentifiedObject.name ?bus.
 OPTIONAL {?pep c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?s.
 ?pep c:PowerElectronicsConnectionPhase.phase ?phsraw.
	bind(strafter(str(?phsraw),\"SinglePhaseKind.\") as ?phs) } } ORDER BY ?name ?phs
 } GROUP BY ?name ?uname ?bus ?ratedS ?ratedU ?ratedE ?storedE ?p ?q ?eqid ?fdrid
 ORDER BY ?name
"""

qstrSync = constants.prefix + """SELECT ?name ?bus ?ratedS ?ratedU ?p ?q (group_concat(distinct ?phs;separator=\"\") as ?phases) ?eqid ?fdrid WHERE {
	SELECT ?name ?bus ?ratedS ?ratedU ?p ?q ?eqid ?fdrid ?phs WHERE {""" + fidselect + """
 ?s r:type c:SynchronousMachine.
 ?s c:IdentifiedObject.name ?name.
 ?s c:IdentifiedObject.mRID ?eqid. 
 ?s c:SynchronousMachine.ratedS ?ratedS.
 ?s c:SynchronousMachine.ratedU ?ratedU.
 ?s c:SynchronousMachine.p ?p.
 ?s c:SynchronousMachine.q ?q. 
 ?t c:Terminal.ConductingEquipment ?s.
 ?t c:Terminal.ConnectivityNode ?cn. 
 ?cn c:IdentifiedObject.name ?bus.
 OPTIONAL {?smp c:SynchronousMachinePhase.SynchronousMachine ?s.
 ?smp c:SynchronousMachinePhase.phase ?phsraw.
   bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) } } ORDER BY ?name ?phs
 } GROUP BY ?name ?bus ?ratedS ?ratedU ?p ?q ?eqid ?fdrid
 ORDER BY ?name
"""

solarDER = {}
storageDER = {}
syncDER = {}

def load_all_DER():
	sparql.setQuery(qstrSolar)
	ret = sparql.query()
	for b in ret.bindings:
		name = b['name'].value
		uname = b['uname'].value
		bus = b['bus'].value
		phases = b['phases'].value
		ratedS = b['ratedS'].value
		ratedU = b['ratedU'].value
		p = b['p'].value
		q = b['q'].value
		eqid = b['eqid'].value
		fdrid = b['fdrid'].value
		solarDER[eqid] = {'name':name, 'uname':uname, 'bus':bus, 'phases':phases, 'fdrid':fdrid,
											'ratedS':float(ratedS), 'ratedU':float(ratedU), 'p':float(p), 'q':float(q)}

	sparql.setQuery(qstrStorage)
	ret = sparql.query()
	for b in ret.bindings:
		name = b['name'].value
		uname = b['uname'].value
		bus = b['bus'].value
		phases = b['phases'].value
		ratedS = b['ratedS'].value
		ratedU = b['ratedU'].value
		ratedE = b['ratedE'].value
		storedE = b['storedE'].value
		p = b['p'].value
		q = b['q'].value
		eqid = b['eqid'].value
		fdrid = b['fdrid'].value
		storageDER[eqid] = {'name':name, 'uname':uname, 'bus':bus, 'phases':phases, 'fdrid':fdrid,
											'ratedS':float(ratedS), 'ratedU':float(ratedU), 
											'ratedE':float(ratedE), 'storedE':float(storedE), 'p':float(p), 'q':float(q)}

	sparql.setQuery(qstrSync)
	ret = sparql.query()
	for b in ret.bindings:
		name = b['name'].value
		bus = b['bus'].value
		phases = b['phases'].value
		ratedS = b['ratedS'].value
		ratedU = b['ratedU'].value
		p = b['p'].value
		q = b['q'].value
		eqid = b['eqid'].value
		fdrid = b['fdrid'].value
		syncDER[eqid] = {'name':name, 'bus':bus, 'phases':phases, 'fdrid':fdrid,
										 'ratedS':float(ratedS), 'ratedU':float(ratedU), 'p':float(p), 'q':float(q)}

def _main():
	load_all_DER()
	groups = {}
	groups['AllSolar'] = grp.derms_group ('Photovoltaics')
	for key, val in solarDER.items():
		groups['AllSolar'].add_DER (key, val)

	groups['AllStorage'] = grp.derms_group ('Batteries')
	for key, val in storageDER.items():
		groups['AllStorage'].add_DER (key, val)

	groups['AllSync'] = grp.derms_group ('Machines')
	for key, val in syncDER.items():
		groups['AllSync'].add_DER (key, val)

	print ('Initial DER Groups Loaded from Blazegraph')
	print ('Key Description mRID Count totalS[kVA] totalP[kW]')
	for key, val in groups.items():
		print (key, val.desc, val.ID, val.get_count(), 0.001 * val.get_total_ratedS(), 0.001 * val.get_total_p())

if __name__ == "__main__":
	_main()

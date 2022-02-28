def si_works_query():
    query = """
    PREFIX edan: <http://edan.si.edu/saam/id/ontologies/>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT ?artist (SAMPLE(?label) as ?sampleLabel) ?image ?shortBio ?deathDate ?birthDate ?nationalityLabel ?workRepresentation ?work
    WHERE {
    ?artist cidoc:P1_is_identified_by ?displayName .
    ?displayName rdfs:label ?label .
    ?artist edan:PE_has_main_representation ?image .
    OPTIONAL { ?artist edan:PE_has_note_luceartistbio ?shortBio . }

    OPTIONAL {?artist cidoc:P100i_died_in ?P100i_died_in .
    ?P100i_died_in cidoc:P4_has_time-span ?deathSpan .
    ?deathSpan cidoc:P82_at_some_time_within ?deathDate } .

    OPTIONAL {?artist cidoc:P98i_was_born ?P98i_was_born .
    ?P98i_was_born cidoc:P4_has_time-span ?birthSpan .
    ?birthSpan cidoc:P82_at_some_time_within ?birthDate } .

    OPTIONAL {?artist cidoc:P107i_is_current_or_former_member_of ?nationality .
    ?nationality skos:prefLabel ?nationalityLabel } .

    ?production cidoc:P14_carried_out_by ?artist .
    ?production cidoc:P108_has_produced ?work .
    ?work cidoc:P138i_has_representation ?workRepresentation
    }
    GROUP BY ?artist ?image ?shortBio ?deathDate ?birthDate ?nationalityLabel ?workRepresentation ?work
    LIMIT 7000
    """
    return query

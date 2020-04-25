
SEQUENCE_RECORD={
    "namespace": "roskinlab",
    "name": "sequence_record",
    "aliases": ["seq_record", "seq_rec", "record"],
    "type": "record",
    "fields": [
        {
            "name": "name",
            "type": "string"
        },
        {
            "name": "source",
            "type": ["null", "string"]
        },
        {
            "name": "subject",
            "type": ["null", "string"]
        },
        {
            "name": "sample",
            "type": ["null", "string"]
        },
        {
            "name": "sequence",
            "type": {
                "namespace": "roskinlab.sequence_record",
                "name": "sequence",
                "aliases": ["seq"],
                "type": "record",
                "fields": [
                    {
                        "name": "sequence",
                        "type": "string"
                    },
                    {
                        "name": "qual",
                        "type": "string"
                    },
                    {
                        "name": "annotations",
                        "type": {
                            "type": "map",
                            "values": ["null", "string", "int", "float", "boolean"]
                        }
                    },
                    {
                        "name": "ranges",
                        "type": {
                            "type": "map",
                            "values": {
                                "namespace": "roskinlab",
                                "type": "record",
                                "name": "range",
                                "fields": [
                                    {
                                        "name": "start",
                                        "type": ["null", "int"]
                                    },
                                    {
                                        "name": "stop",
                                        "type": ["null", "int"]
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        },
        {
            "name": "parses",
            "type": {
                "type": "map",
                "values": ["null", {
                    "namespace": "roskinlab",
                    "name": "parse",
                    "aliases": ["parse_record"],
                    "type": "record",
                    "fields": [
                        {
                            "name": "chain",
                            "type": ["null", {
                                "namespace": "roskinlab.parse",
                                "name": "chain_type",
                                "aliases": ["chain"],
                                "type": "enum",
                                "symbols": ["VH", "VK", "VL", "VB", "VA", "VD", "VG"]
                            }]
                        },
                        {
                            "name": "has_stop_codon",
                            "type": ["null", "boolean"]
                        },
                        {
                            "name": "v_j_in_frame",
                            "type": ["null", "boolean"]
                        },
                        {
                            "name": "positive_strand",
                            "type": ["null", "boolean"]
                        },
                        {
                            "name": "alignments",
                            "type": {
                                "type": "array",
                                "items": {
                                    "namespace": "roskinlab.parse",
                                    "name": "alignment",
                                    "aliases": ["align"],
                                    "type": "record",
                                    "fields": [
                                        {
                                            "name": "type",
                                            "type": {
                                                "namespace": "roskinlab.parse",
                                                "name": "alignment_type",
                                                "aliases": ["align_type"],
                                                "type": "enum",
                                                "symbols": ["Q", "L", "V", "D", "J", "C", "T", "S"]
                                            }
                                        },
                                        {
                                            "name": "name",
                                            "type": "string"
                                        },
                                        {
                                            "name": "score",
                                            "type": "float"
                                        },
                                        {
                                            "name": "e_value",
                                            "type": "float"
                                        },
                                        {
                                            "name": "range",
                                            "type": "roskinlab.range"
                                        },
                                        {
                                            "name": "padding",
                                            "type": "roskinlab.range"
                                        },
                                        {
                                            "name": "alignment",
                                            "type": "string"
                                        }
                                    ]
                                }
                            }
                        },
                        {
                            "name": "ranges",
                            "type": {
                                "type": "map",
                                "values": "roskinlab.range"
                            }
                        }
                    ]
                }]
            }
        },
        {
            "name": "lineages",
            "type": {
                "type": "map",
                "values": "string"
            }
        }
    ]
}

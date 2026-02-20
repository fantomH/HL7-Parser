# ------------------------------------------------------------------------ INFO
# [/HL7_parser/HL7_parser.py]
# author        : Pascal Malouin (https://github.com/fantomH)
# created       : 2025-12-10 16:28:41 UTC
# updated       : 2026-02-18 12:08:44 UTC
# description   : HL7 parser.

"""
Medical Imaging HL7 parser.
"""

import argparse
import json
import re
import sys

from charset_normalizer import from_path

MSH_FIELDS = {
    1:  "Field Separator",
    2:  "Encoding Characters",
    3:  "Sending Application",
    4:  "Sending Facility",
    5:  "Receiving Application",
    6:  "Receiving Facility",
    7:  "Date/Time of Message",
    8:  "Security",
    9:  "Message Type",
    10: "Message Control ID",
    11: "Processing ID",
    12: "Version ID",
    13: "Sequence Number",
    14: "Continuation Pointer",
    15: "Accept Acknowledgment Type",
    16: "Application Acknowledgment Type",
    17: "Country Code",
    18: "Character Set",
    19: "Principal Language of Message",
    20: "Alternate Character Set Handling Scheme",
    21: "Message Profile Identifier"
}

PID_FIELDS = {
    1:  "Set ID - PID",
    2:  "Patient ID (External ID)",
    3:  "Patient Identifier List",
    4:  "Alternate Patient ID",
    5:  "Patient Name",
    6:  "Mother's Maiden Name",
    7:  "Date/Time of Birth",
    8:  "Administrative Sex",
    9:  "Patient Alias",
    10: "Race",
    11: "Patient Address",
    12: "County Code",
    13: "Phone Number - Home",
    14: "Phone Number - Business",
    15: "Primary Language",
    16: "Marital Status",
    17: "Religion",
    18: "Patient Account Number",
    19: "SSN Number",
    20: "Driver's License Number",
    21: "Mother's Identifier",
    22: "Ethnic Group",
    23: "Birth Place",
    24: "Multiple Birth Indicator",
    25: "Birth Order",
    26: "Citizenship",
    27: "Veterans Military Status",
    28: "Nationality",
    29: "Patient Death Date/Time",
    30: "Patient Death Indicator"
}

PV1_FIELDS = {
    1: "Set ID – PV1",
    2: "Patient Class",
    3: "Assigned Patient Location",
    4: "Admission Type",
    5: "Preadmit Number",
    6: "Prior Patient Location",
    7: "Attending Doctor",
    8: "Referring Doctor",
    9: "Consulting Doctor",
    10: "Hospital Service",
    11: "Temporary Location",
    12: "Preadmit Test Indicator",
    13: "Re-admission Indicator",
    14: "Admit Source",
    15: "Ambulatory Status",
    16: "VIP Indicator",
    17: "Admitting Doctor",
    18: "Patient Type",
    19: "Visit Number",
    20: "Financial Class",
    21: "Charge Price Indicator",
    22: "Courtesy Code",
    23: "Credit Rating",
    24: "Contract Code",
    25: "Contract Effective Date",
    26: "Contract Amount",
    27: "Contract Period",
    28: "Interest Code",
    29: "Transfer to Bad Debt Code",
    30: "Transfer to Bad Debt Date",
    31: "Bad Debt Agency Code",
    32: "Bad Debt Transfer Amount",
    33: "Bad Debt Recovery Amount",
    34: "Delete Account Indicator",
    35: "Delete Account Date",
    36: "Discharge Disposition",
    37: "Discharged to Location",
    38: "Diet Type",
    39: "Servicing Facility",
    40: "Bed Status",
    41: "Account Status",
    42: "Pending Location",
    43: "Prior Temporary Location",
    44: "Admit Date/Time",
    45: "Discharge Date/Time",
    46: "Current Patient Balance",
    47: "Total Charges",
    48: "Total Adjustments",
    49: "Total Payments",
    50: "Alternate Visit ID",
    51: "Visit Indicator",
    52: "Other Healthcare Provider"
}

ORC_FIELDS = {
    1:  "Order Control",
    2:  "Placer Order Number",
    3:  "Filler Order Number",
    4:  "Placer Group Number",
    5:  "Order Status",
    6:  "Response Flag",
    7:  "Quantity/Timing",
    8:  "Parent Order",
    9:  "Date/Time of Transaction",
    10: "Entered By",
    11: "Verified By",
    12: "Ordering Provider",
    13: "Enterer's Location",
    14: "Call Back Phone Number",
    15: "Order Effective Date/Time",
    16: "Order Control Code Reason",
    17: "Entering Organization",
    18: "Entering Device",
    19: "Action By"
}

OBR_FIELDS = {
    1: "Set ID – OBR",
    2: "Placer Order Number",
    3: "Filler Order Number",
    4: "Universal Service ID",
    5: "Priority",
    6: "Requested Date/time",
    7: "Observation Date/Time",
    8: "Observation End Date/Time",
    9: "Collection Volume",
    10: "Collector Identifier",
    11: "Specimen Action Code",
    12: "Danger Code",
    13: "Relevant Clinical Info.",
    14: "Specimen Received Date/Time",
    15: "Specimen Source",
    16: "Ordering Provider",
    17: "Order Callback Phone Number",
    18: "Placer field 1",
    19: "Placer field 2",
    20: "Filler Field 1",
    21: "Filler Field 2",
    22: "Results Rpt/Status Chng – Date/Time",
    23: "Charge to Practice",
    24: "Diagnostic Serv Sect ID",
    25: "Result Status",
    26: "Parent Result",
    27: "Quantity/Timing",
    28: "Result Copies To",
    29: "Parent",
    30: "Transportation Mode",
    31: "Reason for Study",
    32: "Principal Result Interpreter",
    33: "Assistant Result Interpreter",
    34: "Technician",
    35: "Transcriptionist",
    36: "Scheduled Date/Time",
    37: "Number of Sample Containers",
    38: "Transport Logistics of Collected Sample",
    39: "Collector’s Comment",
    40: "Transport Arrangement Responsibility",
    41: "Transport Arranged",
    42: "Escort Required",
    43: "Planned Patient Transport Comment"
}

OBX_FIELDS = {
    1:  "Set ID - OBX",
    2:  "Value Type",
    3:  "Observation Identifier",
    4:  "Observation Sub-ID",
    5:  "Observation Value",
    6:  "Units",
    7:  "References Range",
    8:  "Abnormal Flags",
    9:  "Probability",
    10: "Nature of Abnormal Test",
    11: "Observation Result Status",
    12: "Effective Date of Reference Range",
    13: "User Defined Access Checks",
    14: "Date/Time of Observation",
    15: "Producer's ID",
    16: "Responsible Observer",
    17: "Observation Method"
}

HL7_FIELDS = {
    "MSH": MSH_FIELDS,
    "PID": PID_FIELDS,
    "PV1": PV1_FIELDS,
    "ORC": ORC_FIELDS,
    "OBR": OBR_FIELDS,
    "OBX": OBX_FIELDS,
}


def read_file(filepath):
    """
    Read an HL7 file.
    Will try to guess the encoding.
    """
    
    try:
        return open(filepath, "r", encoding="utf-8").read()
    except UnicodeDecodeError:
        det = from_path(filepath, threshold=1.0).best()
        enc = det.encoding if det else "latin-1"
        return open(filepath, "r", encoding=enc, errors="replace").read()

def parse_hl7_messages(text):
    """
    Parses the HL7 text.
    Will fix the text as needed and separate the messages, if multiple messages
    found.
    """

    # --- Replace segment separators.
    text = text.replace('\r\n', '__ENDSEG__').replace('\r', '__ENDSEG__').replace('\n', '__ENDSEG__')
    # --- Remove Minimal Lower Layer Protocol ( MLLP).
    text = text.replace('\x0b', '').replace('\x1c', '')
    # --- Remove empty lines.
    text = re.sub(r"(?:__ENDSEG__){2,}", "", text)

    # --- Split into messages based on MSH (start of a new HL7 message).
    raw_messages = re.split(r'(?=MSH)', text, flags=re.MULTILINE)

    # --- Reconstructing.
    cleaned_messages = []
    for raw_message in raw_messages:
        if not raw_message.strip():
            continue
        # --- Remove empty string in list.
        cleaned_message = [x for x in re.split(r'__ENDSEG__', raw_message) if x[0:3].isalnum() and x[0:3].isupper() and len(x) >=4]
        cleaned_messages.append(cleaned_message)

    return cleaned_messages

def get_field_separator(msh_seg):
    """
    Find the fields separator.
    """

    field_sep = msh_seg[3]
    enc_characters = msh_seg[4:8]

    return field_sep, enc_characters

def split_segment(segment: str, field_separator="|") -> list:
    """
    Split a segment into a list of fields.
    Will try to find the separator as defined in MSH, otherwise will use "|" as
    default.
    """

    fields = segment.split(field_separator)
    return fields

def hl7_as_dict(message: list, _clean=False) -> list:
    """
    Returns a list of messages structured into dictionaries.
    """

    message_list = []
    for seg in message:
        segment_name = seg[:3]
        segment = {segment_name: {}}
        if seg.startswith('MSH'):
            field_sep, enc_characters = get_field_separator(seg)
            segment[segment_name][f"{segment_name}-1"] = {
                'description': HL7_FIELDS.get('MSH', {}).get(1),
                'value': f'{field_sep}'
                }
            segment[segment_name][f"{segment_name}-2"] = {
                'description': HL7_FIELDS.get('MSH', {}).get(2),
                'value': f'{enc_characters}'
                }
            fields = split_segment(seg, field_separator=field_sep)
            for i, field, in enumerate(fields[2:], start=3):
                if field == "" and _clean:
                    continue
                segment[segment_name][f"{segment_name}-{i}"] = {
                    'description': HL7_FIELDS.get(f'{segment_name}', {}).get(i, "UNDEFINED"),
                    'value': f"{field}"
                    }
            message_list.append(segment)
        else:
            fields = split_segment(seg, field_separator=field_sep)
            for i, field, in enumerate(fields[1:], start=1):
                if field == "" and _clean:
                    continue
                segment[segment_name][f"{segment_name}-{i}"] = {
                    'description': HL7_FIELDS.get(f"{segment_name}", {}).get(i, "UNDEFINED"),
                    'value': f"{field}"
                    }
            message_list.append(segment)
            
    return message_list

def display_plain(messages):
    """
    Prints each segments of each messages.
    """

    for i, msg in enumerate(messages):
        print(f"--- HL7 Message {i+1} ---\n")
        for seg in msg:
            print(seg)
        print("=" * 40)

def display_human(messages, clean=False, show_description=False):
    """
    Prints each messages in a human readable format.
    """

    messages = [hl7_as_dict(msg) for msg in messages]

    for i, msg, in enumerate(messages):
        print(f"--- HL7 Message {i+1} ---\n")
        for seg in msg:
            for k, v in seg.items():
                segment = seg.get(k)
                for k, v in segment.items():
                    if clean and not v['value'].strip():
                        continue
                    if show_description:
                        print(f"{k:7}({v['description']})  {v['value']}")
                    else:
                        print(f"{k:7} {v['value']}")
            print()
        print("=" * 40)

def display_as_json(messages):
    """
    Prints messages as JSON.
    """

    messages_for_json = [hl7_as_dict(msg, _clean=True) for msg in messages]

    print(json.dumps(messages_for_json, indent=4, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(description="HL7 Message Parser for medical imaging.")
    parser.add_argument("filepath", help="Path to HL7 file.")
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Display plain HL7 messages."
        )
    parser.add_argument(
        "--human",
        action="store_true",
        help="Display human readable HL7 messages."
        )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Display HL7 messages as JSON."
        )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove empty HL7 fields from display."
        )
    parser.add_argument(
        "--show-description",
        action="store_true",
        help="Show HL7 fields description."
        )

    args = parser.parse_args()
    filepath = args.filepath

    raw_text = read_file(filepath)

    messages = parse_hl7_messages(raw_text)

    if args.plain:
        display_plain(messages)
        sys.exit(0)

    if args.human:
        display_human(messages, clean=args.clean, show_description=args.show_description)
        exit(0)
        # if args.clean:
            # display_human(messages, clean=True)
            # exit(0)
        # else:
            # display_human(messages)
            # exit(0)

    if args.json:
        if args.clean:
            pass
        else:
            display_as_json(messages)
            exit(0)

    print(messages)

if __name__ == "__main__":
    main()

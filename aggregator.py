import xml.etree.ElementTree as ET
import json
import os

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root

def xml_to_dict(element):
    node = {}
    if element.items():
        node.update(dict(element.items()))
    if element.text and element.text.strip():
        node['text'] = element.text.strip()
    for child in element:
        child_dict = xml_to_dict(child)
        if child.tag in node:
            if not isinstance(node[child.tag], list):
                node[child.tag] = [node[child.tag]]
            node[child.tag].append(child_dict)
        else:
            node[child.tag] = child_dict    
    return node

def dict_to_json(data):
    return json.dumps(data, indent=4)

def process_annotation_object(obj):
    object = {}            
    object['name'] = obj['name']['text']                         
    for key in ['deleted', 'verified']:
        object[key] = bool(int(obj[key]['text']))
    object['occluded'] = True
    if obj['occluded']['text'] == 'no':
        object['occluded'] = False
    object['id'] = int(obj['id']['text'])
    object['type'] = obj['type']['text']
    object['polygon'] = [float(obj['polygon']['pt'][0]['x']['text']),
                        float(obj['polygon']['pt'][0]['y']['text']),
                        float(obj['polygon']['pt'][1]['x']['text']),
                        float(obj['polygon']['pt'][2]['y']['text']),
                        ]
    object['attributes'] = {}
    for attribute in obj['attributes']['text'].split(','):
        key, value = attribute.split('=')
        key = key[key.rfind(' ') + 1:].lower()
        object['attributes'][key] = value

    return object

def prune_dict(big_dict):
    image_annotations = {}    
    image_annotations['filename'] = big_dict['filename']['text']
    image_annotations['source'] = big_dict['source']['sourceAnnotation']['text']
    image_annotations['size'] = {}
    image_annotations['size']['width'] = int(big_dict['imagesize']['nrows']['text'])
    image_annotations['size']['height'] = int(big_dict['imagesize']['ncols']['text'])    
    if type(big_dict['object']) is list:
        image_annotations['annotations'] = []
        for obj in big_dict['object']:            
            image_annotations['annotations'].append(process_annotation_object(obj))
    else:
        image_annotations['annotations'] = [process_annotation_object(big_dict['object'])]
    return image_annotations

def driver(export_dir, save_dir='annotations.json'):
    aggregated_annotations = {'images': []}
    for root, folders, files in os.walk(export_dir):
        for file in files:
            if not 'xml' in file:
                continue
            aggregated_annotations['images'].append(prune_dict(xml_to_dict(parse_xml(os.path.join(root, file)))))
    with open(save_dir, 'w', encoding='utf-8') as f:
        json.dump(aggregated_annotations, f)

    print(f'Annotations from {len(aggregated_annotations["images"])} images transformed and saved to {save_dir}.')

driver('S48-E4833_Rosita-And-Elmo-Teach-Yoga')

        

from app.questionnaire.rules import evaluate_when_rules


def _choose_variant(
    block,
    schema,
    metadata,
    answer_store,
    list_store,
    variants_key,
    single_key,
    current_location=None,
):
    if block.get(single_key):
        return block[single_key]

    for variant in block.get(variants_key, []):
        when_rules = variant.get('when', [])
        if evaluate_when_rules(
            when_rules,
            schema,
            metadata,
            answer_store,
            list_store,
            current_location=current_location,
        ):
            return variant[single_key]


def choose_question_to_display(
    block, schema, metadata, answer_store, list_store, current_location=None
):
    return _choose_variant(
        block,
        schema,
        metadata,
        answer_store,
        list_store,
        variants_key='question_variants',
        single_key='question',
        current_location=current_location,
    )


def choose_content_to_display(
    block, schema, metadata, answer_store, list_store, current_location=None
):
    return _choose_variant(
        block,
        schema,
        metadata,
        answer_store,
        list_store,
        variants_key='content_variants',
        single_key='content',
        current_location=current_location,
    )


def transform_variants(
    block, schema, metadata, answer_store, list_store, current_location=None
):
    output_block = block.copy()

    if 'question_variants' in block:
        question = choose_question_to_display(
            block, schema, metadata, answer_store, list_store, current_location
        )
        output_block.pop('question_variants', None)
        output_block.pop('question', None)

        output_block['question'] = question

    if 'content_variants' in block:
        content = choose_content_to_display(
            block, schema, metadata, answer_store, list_store, current_location
        )
        output_block.pop('content_variants', None)
        output_block.pop('content', None)

        output_block['content'] = content

    if block['type'] in ('ListCollector', 'PrimaryPersonListCollector'):
        list_operations = ['add_block', 'edit_block', 'remove_block']
        for list_operation in list_operations:
            if block.get(list_operation):
                output_block[list_operation] = transform_variants(
                    block[list_operation],
                    schema,
                    metadata,
                    answer_store,
                    list_store,
                    current_location,
                )

    return output_block


def get_answer_ids_in_block(block):
    question = block['question']
    answer_ids = []
    for answer in question['answers']:
        answer_ids.append(answer['id'])

    return answer_ids
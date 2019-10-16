local placeholders = import '../../../lib/placeholders.libsonnet';
local rules = import 'rules.libsonnet';

local question(title) = {
  id: 'employment-status-question',
  title: title,
  description: '<em>Tell respondent to turn to <strong>Showcard 10</strong></em>',
  type: 'MutuallyExclusive',
  mandatory: true,
  guidance: {
    contents: [
      {
        description: 'Include casual or temporary work, even if only for one hour',
      },
    ],
  },
  answers: [
    {
      id: 'employment-status-answer',
      mandatory: false,
      type: 'Checkbox',
      options: [
        {
          label: 'Working as an employee',
          value: 'Working as an employee',
        },
        {
          label: 'Self-employed or freelance',
          value: 'Self-employed or freelance',
        },
        {
          label: 'Temporarily away from work ill, on holiday or temporarily laid off',
          value: 'Temporarily away from work ill, on holiday or temporarily laid off',
        },
        {
          label: 'On maternity or paternity leave',
          value: 'On maternity or paternity leave',
        },
        {
          label: 'Doing any other kind of paid work',
          value: 'Doing any other kind of paid work',
        },
      ],
    },
    {
      id: 'employment-status-answer-exclusive',
      type: 'Checkbox',
      mandatory: false,
      options: [
        {
          label: 'None of these apply',
          value: 'None of these apply',
        },
      ],
    },
  ],
};

local nonProxyTitle = 'During the week of 7 to 13 October 2019, were you doing any of the following?';
local proxyTitle = {
  text: 'During the week of 7 to 13 October 2019, was {person_name} doing any of the following?',
  placeholders: [
    placeholders.personName,
  ],
};

{
  type: 'Question',
  id: 'employment-status',
  question_variants: [
    {
      question: question(nonProxyTitle),
      when: [rules.isNotProxy],
    },
    {
      question: question(proxyTitle),
      when: [rules.isProxy],
    },
  ],
  routing_rules: [
    {
      goto: {
        block: 'employment-type',
        when: [{
          id: 'employment-status-answer-exclusive',
          condition: 'set',
        }],
      },
    },
    {
      goto: {
        block: 'another-uk-address',
      },
    },
  ],
}

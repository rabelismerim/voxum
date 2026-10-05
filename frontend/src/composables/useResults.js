export const notNaN = num =>
  Number.isNaN(num) ? 0 : num
export const getPercentage = (value, total) =>
  notNaN(value / (total ?? 1)) * 100

const abstentionLabels = ['abstenção', 'abstencao', 'talvez']

const sortChoices = choices => {
  const yesChoiceIndex = choices
    .findIndex(({ label }) => 'sim'.includes(label.toLowerCase()))
  const yesChoice = choices[yesChoiceIndex]
  const noChoiceIndex = choices
    .findIndex(({ label }) => 'não,nao'.includes(label.toLowerCase()))
  const noChoice = choices[noChoiceIndex]
  const abstentionChoiceIndex = choices
    .findIndex(({ label }) => abstentionLabels.includes(label.toLowerCase()))
  const abstentionChoice = choices[abstentionChoiceIndex]
  return [
    yesChoice && { label: 'Sim', ...yesChoice },
    noChoice && { label: 'Não', ...noChoice },
    ...choices
      ?.filter((_, index) => ![yesChoiceIndex, noChoiceIndex, abstentionChoiceIndex].includes(index))
      ?.sort(({ label: a }, { label: b }) => a < b ? -1 : 1),
    abstentionChoice && { label: 'Abstenção', ...abstentionChoice },
  ].filter(e => !!e)
}

export const mapResults = (results, withAbstention) => {
  const data = results
    .reduce((acc, {
      choices: useChoices,
      name,
      countQualifiedCreditors: qualifiedCreditors,
      totalCreditValue: qualifiedAmount,
    }) => {
      const className = `classe${name.split('-').at(0).trim().toUpperCase().split(' ').at(1)}`
      const choices = sortChoices(useChoices
        .filter(({ value }) =>
          withAbstention ? true : !abstentionLabels.includes(value.toLowerCase()))
        .map(({ value, countVoters, totalVotersCreditValue }) => ({
          label: value,
          creditors: countVoters ?? 0,
          amount: totalVotersCreditValue ?? 0,
        })))
      const abstentionChoice = useChoices
        .find(({ value }) => abstentionLabels.includes(value.toLowerCase()))
      const votedCreditors = choices.reduce((acc, { creditors }) => acc + creditors, 0)
      const votedAmount = choices.reduce((acc, { amount }) => acc + amount, 0)
      acc[className] = {
        name,
        choices,
        abstentionChoice: {
          label: 'Abstenção',
          creditors: abstentionChoice?.countVoters ?? 0,
          amount: abstentionChoice?.totalVotersCreditValue ?? 0,
        },
        votedCreditors,
        qualifiedCreditors,
        votedAmount,
        qualifiedAmount,
      }
      acc.total = {
        votedCreditors: acc.total.votedCreditors + votedCreditors,
        qualifiedCreditors: acc.total.qualifiedCreditors + qualifiedCreditors,
        votedAmount: acc.total.votedAmount + votedAmount,
        qualifiedAmount: acc.total.qualifiedAmount + qualifiedAmount,
        abstentionChoice: {
          label: 'Abstenção',
          creditors: acc.total.qualifiedCreditors - acc.total.votedCreditors,
          amount: acc.total.qualifiedAmount - acc.total.votedAmount,
        }
      }
      return acc
    }, {
      total: {
        votedCreditors: 0,
        qualifiedCreditors: 0,
        votedAmount: 0,
        qualifiedAmount: 0
      }
    })
  data.total.choices = sortChoices(Object.values(Object.entries(data)
    ?.filter(([key]) => key !== 'total')
    ?.reduce((acc, [_, { choices }]) => {
      choices.forEach(({ label, creditors, amount }) => {
        if (!acc[label])
          acc[label] = { label, creditors: 0, amount: 0 }
        acc[label].creditors += creditors
        acc[label].amount += amount
      })
      return acc
    }, {})))
  return {
    choices: ['classeI', 'classeII', 'classeIII', 'classeIV']
      .map(classe => data[classe])
      .filter(e => !!e),
    total: data.total,
  }
}
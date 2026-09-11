const $ = (id) => document.getElementById(id);
let schema, parameterValues;
let groups = [], nextId = 0, downloadURLs = [];

function element(tag, attributes = {}, text) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  if (text !== undefined) node.textContent = text;
  return node;
}

function options(select, items) {
  select.replaceChildren(...items.map((item) => element('option', {value: item.id}, item.label)));
}

function parameterForm(container, parameters) {
  container.replaceChildren();
  const editors = parameters.map((parameter) => {
    const id = `parameter-${++nextId}`;
    const field = element('div', {class: 'field'});
    field.append(element('label', {for: id}, `${parameter.name}${parameter.required ? ' *' : ''}`));
    const hint = element('p', {class: 'hint', id: `${id}-hint`}, parameter.description);
    let input;
    if (parameter.type === 'bool') {
      input = element('select');
      const choices = [{id: 'true', label: 'True'}, {id: 'false', label: 'False'}];
      if (!parameter.required) choices.unshift({id: '', label: 'Use default'});
      options(input, choices);
      if (parameter.required) input.value = 'false';
    } else {
      const numeric = ['natural', 'integer', 'int_pos'].includes(parameter.type);
      input = element('input', {type: numeric ? 'number' : 'text'});
      if (numeric) {
        input.step = '1';
        if (parameter.minimum !== undefined) input.min = String(parameter.minimum);
        if (parameter.required) input.value = String(parameter.minimum ?? 0);
      }
      input.placeholder = parameter.type === 'list_int_pos' ? 'e.g. 1, 3, 5' : parameter.required ? '' : 'Use default';
    }
    input.id = id;
    input.required = parameter.required;
    input.dataset.parameter = parameter.name;
    input.setAttribute('aria-describedby', hint.id);
    field.append(hint, input);
    container.append(field);
    return [parameter.name, input];
  });
  return () => Object.fromEntries(editors.filter(([, input]) => input.value.trim() !== '').map(([name, input]) => [name, input.value.trim()]));
}

function clearError() {
  $('error').hidden = true;
  $('error').textContent = '';
}

function refreshCommand() {
  const command = schema.commands.find((command) => command.id === $('command').value);
  $('command-description').textContent = command.description;
  parameterValues = parameterForm($('parameters'), command.parameters);
  $('dimensions').replaceChildren(...command.dimensions.map((dimension) => {
    const label = element('label', {class: 'check'});
    label.append(element('input', {type: 'checkbox', 'data-name': dimension.name, 'data-kind': dimension.kind}), document.createTextNode(dimension.label));
    return label;
  }));
  clearError();
}

function refreshAPI() {
  $('range-fields').hidden = $('api').value !== 'range';
  clearError();
}

function addRestriction(group) {
  const row = element('div', {class: 'restriction-row'});
  const header = element('div', {class: 'restriction-heading'});
  const field = element('div', {class: 'field'});
  const id = `restriction-${++nextId}`;
  const picker = element('select', {id});
  options(picker, schema.restrictions);
  field.append(element('label', {for: id}, 'Restriction'), picker);
  const remove = element('button', {type: 'button', class: 'quiet', 'aria-label': 'Remove restriction'}, 'Remove');
  header.append(field, remove);
  const parameters = element('div', {class: 'parameters'});
  row.append(header, parameters);
  const item = {row, picker, read: null};
  function refresh() {
    item.read = parameterForm(parameters, schema.restrictions.find((restriction) => restriction.id === picker.value).parameters);
  }
  picker.addEventListener('change', refresh);
  remove.addEventListener('click', () => {
    group.rows = group.rows.filter((candidate) => candidate !== item);
    row.remove();
  });
  refresh();
  group.rows.push(item);
  group.body.append(row);
}

function renumberGroups() {
  groups.forEach((group, index) => { group.title.textContent = `Group ${index + 1} · all must pass`; });
}

function addGroup() {
  const node = element('div', {class: 'restriction-group'});
  const header = element('div', {class: 'group-heading'});
  const title = element('h4');
  const remove = element('button', {type: 'button', class: 'quiet', 'aria-label': 'Remove restriction group'}, 'Remove group');
  header.append(title, remove);
  const body = element('div');
  const add = element('button', {type: 'button', class: 'secondary'}, '+ Add restriction');
  node.append(header, body, add);
  const group = {node, title, body, rows: []};
  add.addEventListener('click', () => addRestriction(group));
  remove.addEventListener('click', () => {
    groups = groups.filter((candidate) => candidate !== group);
    node.remove();
    renumberGroups();
  });
  groups.push(group);
  $('restriction-groups').append(node);
  renumberGroups();
  addRestriction(group);
}

function tablePanel(table) {
  const node = element('table');
  node.append(element('caption', {}, table.label || 'Rendered range table'));
  const head = element('thead'), header = element('tr');
  header.append(element('th', {scope: 'col'}, `${table.row_dimension} / ${table.column_dimension}`));
  for (let column = table.column_bounds[0]; column <= table.column_bounds[1]; column++) {
    header.append(element('th', {scope: 'col'}, `${table.column_dimension}=${column}`));
  }
  head.append(header);
  const body = element('tbody');
  table.data.forEach((values, index) => {
    const row = element('tr');
    row.append(element('th', {scope: 'row'}, `${table.row_dimension}=${table.row_bounds[0] + index}`));
    values.forEach((value) => row.append(element('td', {}, String(value))));
    body.append(row);
  });
  node.append(head, body);
  return node;
}

function renderTabs(views, selected = 0) {
  const tabs = $('result-tabs'), panels = $('result-panels');
  tabs.replaceChildren();
  panels.replaceChildren();
  const buttons = [], sections = [];
  function activate(index, focus = false) {
    buttons.forEach((button, item) => {
      button.setAttribute('aria-selected', String(item === index));
      button.tabIndex = item === index ? 0 : -1;
      sections[item].hidden = item !== index;
    });
    if (focus) buttons[index].focus();
  }
  views.forEach((view, index) => {
    const button = element('button', {type: 'button', role: 'tab', id: `tab-${index}`, 'aria-controls': `panel-${index}`}, view.label);
    const panel = element('div', {class: 'panel', role: 'tabpanel', id: `panel-${index}`, 'aria-labelledby': button.id, tabindex: '0'});
    panel.append(view.content);
    button.addEventListener('click', () => activate(index));
    button.addEventListener('keydown', (event) => {
      let target;
      if (event.key === 'ArrowRight') target = (index + 1) % views.length;
      if (event.key === 'ArrowLeft') target = (index + views.length - 1) % views.length;
      if (event.key === 'Home') target = 0;
      if (event.key === 'End') target = views.length - 1;
      if (target !== undefined) { event.preventDefault(); activate(target, true); }
    });
    buttons.push(button);
    sections.push(panel);
    tabs.append(button);
    panels.append(panel);
  });
  activate(selected);
}

function clearDownloads() {
  downloadURLs.forEach((url) => URL.revokeObjectURL(url));
  downloadURLs = [];
  $('downloads').replaceChildren();
}

function showResult(result) {
  $('summary').textContent = result.summary;
  const views = [{label: 'Text', content: element('pre', {}, result.text.trim())}];
  result.tables.forEach((table, index) => views.push({label: table.label || (result.tables.length === 1 ? 'Table' : `Table ${index + 1}`), content: tablePanel(table)}));
  renderTabs(views, result.tables.length ? 1 : 0);
  for (const file of result.downloads) {
    const url = URL.createObjectURL(new Blob([file.content], {type: file.content_type}));
    downloadURLs.push(url);
    $('downloads').append(element('a', {class: 'download', href: url, download: file.name}, `Download ${file.name}`));
  }
}

$('query-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  if ($('query-fields').disabled) return;
  clearError();
  const payload = {
    api: $('api').value, command: $('command').value,
    parameters: parameterValues(), statistic: $('statistic').value || null,
    output: $('output').value, print_elements: $('print-elements').checked,
    dimensions: [...$('dimensions').querySelectorAll('input:checked')].map((input) => ({name: input.dataset.name, kind: input.dataset.kind})),
    restriction_groups: groups.map((group) => group.rows.map((row) => ({name: row.picker.value, parameters: row.read()}))).filter((group) => group.length),
  };
  $('query-fields').disabled = true;
  $('run').textContent = 'Running…';
  $('status').textContent = 'Running query…';
  document.querySelector('.results').setAttribute('aria-busy', 'true');
  clearDownloads();
  renderTabs([{label: 'Text', content: element('p', {class: 'empty'}, 'Calculating your query…')}]);
  $('summary').textContent = 'Waiting for results.';
  try {
    const response = await fetch('/api/query', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'The query could not be completed.');
    showResult(result);
    $('status').textContent = 'Complete';
  } catch (error) {
    $('status').textContent = 'Failed';
    $('error').textContent = error.message;
    $('error').hidden = false;
    $('summary').textContent = 'The query could not be completed.';
    renderTabs([{label: 'Text', content: element('pre', {}, error.message)}]);
  } finally {
    $('query-fields').disabled = false;
    $('run').textContent = 'Run query';
    document.querySelector('.results').setAttribute('aria-busy', 'false');
  }
});

async function initialize() {
  const empty = element('div', {class: 'empty'});
  empty.append(element('strong', {}, 'Ready to explore'), document.createTextNode('Set up a query and run it to see your results.'));
  renderTabs([{label: 'Text', content: empty}]);
  try {
    const response = await fetch('/api/schema');
    if (!response.ok) throw new Error('Could not load query options.');
    schema = await response.json();
    options($('api'), schema.apis);
    $('api').value = 'point';
    options($('command'), schema.commands);
    options($('statistic'), [{id: '', label: 'Count objects'}, ...schema.statistics]);
    options($('output'), schema.outputs);
    $('command').addEventListener('change', refreshCommand);
    $('api').addEventListener('change', refreshAPI);
    $('add-group').addEventListener('click', addGroup);
    refreshCommand();
    refreshAPI();
    $('query-fields').disabled = false;
    $('status').textContent = 'Ready';
  } catch (error) {
    $('status').textContent = 'Unable to connect';
    $('error').textContent = `${error.message} Check that the local server is running, then reload this page.`;
    $('error').hidden = false;
  }
}

initialize();

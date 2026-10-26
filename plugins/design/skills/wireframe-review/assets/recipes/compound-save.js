// Review-owned application recipe. UI primitives remain owned by base-ui.
// Adapt the snapshot fields and unit ID to the task; do not include view preferences.
const compoundSnapshot = state => ({
  title: state.title,
  format: state.format,
  capacity: state.capacity,
  selected: [...new Set(state.selected)].sort()
});
const compoundIsCurrent = state => Boolean(state.saved) &&
  JSON.stringify(compoundSnapshot(state)) === JSON.stringify(state.saved);
const compoundIsValid = state => state.title.trim().length > 0 &&
  ['basic', 'extended'].includes(state.format) &&
  /^\d+$/.test(state.capacity) && Number(state.capacity) >= 1 && Number(state.capacity) <= 20;
registerPrototype({
  unitId: 'compound-save',
  initialState: {title: 'Planning', format: 'basic', capacity: '4', selected: ['alpha'], saved: null, confirmations: true, filter: ''},
  reduce(state, action) {
    if (action.type === 'edit') return {...state, [action.key]: action.value};
    if (action.type === 'person') return {...state, selected: action.checked
      ? [...new Set([...state.selected, action.id])]
      : state.selected.filter(id => id !== action.id)};
    if (action.type === 'save' && compoundIsValid(state)) return {...state, saved: compoundSnapshot(state)};
    if (action.type === 'restore' && state.saved) return {...state, ...state.saved, selected: [...state.saved.selected]};
    return state;
  },
  render(root, state) {
    for (const id of ['title', 'capacity', 'filter']) {
      const node = root.querySelector('#' + id);
      if (node.value !== state[id]) node.value = state[id];
    }
    for (const id of ['basic', 'extended']) root.querySelector('#' + id).checked = state.format === id;
    root.querySelectorAll('[data-person]').forEach(node => node.checked = state.selected.includes(node.dataset.person));
    root.querySelector('#confirmations').checked = state.confirmations;
    root.querySelector('#capacity-summary').textContent = state.capacity + ' places';
    const names = [...state.selected].sort();
    root.querySelector('#participants').textContent = names.join(', ') || 'None';
    root.querySelector('#filtered-participants').textContent = names.filter(id => id.includes(state.filter.toLowerCase())).join(', ') || 'No matches';
    const current = compoundIsCurrent(state);
    root.querySelector('#status').textContent = current ? 'Saved' : state.saved ? 'Unsaved changes' : 'Unsaved';
    root.querySelector('#confirmation').hidden = !(current && state.confirmations);
    root.querySelector('#restore').disabled = !state.saved;
  },
  bind({root, on, dispatch}) {
    for (const id of ['title', 'capacity', 'filter']) on('input', '#' + id, (event, node) => dispatch({type: 'edit', key: id, value: node.value}));
    on('change', '[name="format"]', (event, node) => dispatch({type: 'edit', key: 'format', value: node.value}));
    on('change', '[data-person]', (event, node) => dispatch({type: 'person', id: node.dataset.person, checked: node.checked}));
    on('change', '#confirmations', (event, node) => dispatch({type: 'edit', key: 'confirmations', value: node.checked}));
    on('click', '#save', () => {
      if (!root.querySelector('form').reportValidity()) return;
      dispatch({type: 'save'});
    });
    on('click', '#restore', () => dispatch({type: 'restore'}));
  }
});

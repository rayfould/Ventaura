// src/styles/index.js
import variables from './variables.module.css';
import base from './base.module.css';
import layout from './layout.module.css';
import states from './states.module.css';

// Import modules
import buttons from './modules/buttons.module.css';
import forms from './modules/forms.module.css';
import navigation from './modules/navigation.module.css';
import boxes from './modules/boxes.module.css';
import eventCard from './modules/EventCard.module.css';  

export default {
    ...variables,
    ...base,
    ...layout,
    ...states,
    ...buttons,
    ...forms,
    ...navigation,
    ...boxes,
    ...eventCard
};

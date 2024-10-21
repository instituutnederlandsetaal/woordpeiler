export const apiURL = window.location.hostname == 'localhost'
    ? window.location.protocol + '//' + window.location.hostname + ':8000' // assume dev
    : window.location.protocol + '//' + window.location.hostname + ':8000' // assume prod


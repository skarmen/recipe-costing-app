const myForm = document.getElementById('myform')

const addIngredient = document.getElementById('add-ingredient')
console.log('addIngredient:', addIngredient)

const dynamicRows = document.getElementById('dynamic-rows')
console.log('dynamicRows:', dynamicRows)

const row = document.getElementsByClassName('ingredient-row')[0]
addIngredient.addEventListener('click', addRow)

const createNewRecipeGroup = document.getElementById('create-new-group')
console.log('createNewRecipeGroup:', createNewRecipeGroup)
createNewRecipeGroup.addEventListener('click', addNewRecipeGroupPrompt)

function addNewRecipeGroupPrompt () {
  const newRecipeGroupInput = prompt('Please enter the new group: ', 'e.g Spring Menu 2020')
  console.log('newRecipeGroupInput:', newRecipeGroupInput)
  if (newRecipeGroupInput === null) {
    return
  }
  const newRecipeGroupInputTrim = newRecipeGroupInput.trim()
  // new group cannot be empty
  if (newRecipeGroupInputTrim == '') {
    alert('Recipe group cannot be empty. Please enter new recipe group name or select one from the dropdown menu.')
    return
  }
  const newRecipeGroupInputLower = newRecipeGroupInputTrim.toLowerCase()
  console.log('newRecipeGroupInputLower:', newRecipeGroupInputLower)
  console.log('existingSheetNames:', existingSheetNames)
  // check if the recipe group name already exists in the spreadhseet
  const existingSheetNamesLower = existingSheetNames.map(item => item.toLowerCase())
  if (existingSheetNamesLower.includes(newRecipeGroupInputLower)) {
    alert('The recipe group already exists in the database. Please enter a different name.')
    return
  }
  const httpRequest = new XMLHttpRequest()
  if (!httpRequest) {
    alert('Giving up :( Cannot create an XMLHTTP instance')
    return false
  }
  httpRequest.onreadystatechange = alertContents
  httpRequest.open('POST', 'submit_new_recipe_group')
  httpRequest.send(newRecipeGroupInputTrim) // add newIngredient to the request
  function alertContents () {
    console.log('httpRequest:', httpRequest)
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      if (httpRequest.status === 200) {
        alert(`Please note that new recipe group '${newRecipeGroupInputTrim}' has been created in the database.`)
        existingSheetNames.push(newRecipeGroupInputLower) // adding to the list for validation
        // TODO: the request was successful, so we need to insert the option into the ingredient list here
        const recipeGroupsOptionsList = document.getElementById('recipe-group')
        const recipeGroupsOptions = `<option value="${newRecipeGroupInputTrim}">${newRecipeGroupInputTrim}</option>`
        recipeGroupsOptionsList.innerHTML += recipeGroupsOptions
      } else {
        alert('There was a problem with the request.')
      }
    }
  }
}

const createNewIngredient = document.getElementById('create-new-ingredient')
console.log('createNewIngredient:', createNewIngredient)
createNewIngredient.addEventListener('click', addNewIngredientPrompt)

function addNewIngredientPrompt () {
  const newIngredientInput = prompt('Please enter the new ingredient: ', 'e.g Raspberries')
  console.log('newIngredientInput:', newIngredientInput)
  // if the prompt window is canceled
  if (newIngredientInput === null) {
    console.log('newIngredientInput:', newIngredientInput)
    return
  }
  const newIngredientInputTrim = newIngredientInput.trim()
  // new ingredient cannot be empty
  if (newIngredientInputTrim == '') {
    alert('Ingredient cannot be empty. Please enter new ingredient name or select one from the dropdown menu.')
    return
  }
  const newIngredientInputLower = newIngredientInputTrim.toLowerCase()
  console.log('newIngredientInputLower:', newIngredientInputLower)
  // check if the ingredient name already exists in the spreadhseet
  const validationIngredientsListLower = validationIngredientsList.map(item => item.toLowerCase())
  console.log('validationListLower:', validationIngredientsListLower)
  if (validationIngredientsListLower.includes(newIngredientInputLower)) {
    alert('This ingredient already exists in the database. Please enter new ingredient name or select one from the dropdown menu.')
    return
  }
  const httpRequest = new XMLHttpRequest()
  if (!httpRequest) {
    alert('Giving up :( Cannot create an XMLHTTP instance')
    return false
  }
  httpRequest.onreadystatechange = alertContents
  httpRequest.open('POST', 'submit_new_ingredient')
  httpRequest.send(newIngredientInputTrim) // add newIngredient to the request

  function alertContents () {
    console.log('httpRequest:', httpRequest)
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      if (httpRequest.status === 200) {
        alert(`Please note that the new ingredient '${newIngredientInputTrim}' has been entered in the database at $0.00 cost. The final recipe cost may vary.`)
        validationIngredientsList.push(newIngredientInputLower) // adding to the list for validation
        console.log('after adding ingredient:', validationIngredientsList)
        // if the request was successful, so we need to insert the option into the ingredient list here
        const ingredientOptionsList = document.getElementById('ingredient-list')
        let ingredientOptions = ''
        ingredientOptions += '<option value="' + newIngredientInputTrim + '"/>'
        ingredientOptionsList.innerHTML += ingredientOptions
      } else {
        alert('There was a problem with the request.')
      }
    }
  }
}
/*
- clones the <div class="ingredient-row"> (the block with all the needed recipe fields)
- appends the clone <div class="ingredient-row"> to a new <div id "dynamic-rows">
- by calling the fucntion as a callback rather than annonymous,
we add one empty set of recipe fields when the page loads, otherwise
the page will load without any fields
*/
function addRow () {
  console.log('Clicked Add Ingredient button')
  const clone = row.cloneNode(true)
  clone.style.display = 'block'
  dynamicRows.appendChild(clone)
  const removeIngredientArray = clone.getElementsByClassName('remove-button')
  const removeIngredientButton = removeIngredientArray[0]
  console.log('removeIngredientButton:', removeIngredientButton)
  removeIngredientButton.addEventListener('click', removeRow)
}
/*
-remove one set of recipe fields at a time
- dynamicRows is the parent
*/
function removeRow (event) {
  // event is an object with details about the event ('click'), target is one of the properties
  console.log('event:', event)
  console.log('Clicked Remove button')
  // note: this might be a span if the button contains a span
  const clickedButton = event.target // get the clicked button
  console.log('clickedButton:', clickedButton)
  const parentDiv = getParent(clickedButton, 'ingredient-row') // the parent of the button that was clicked
  console.log('parentDiv:', parentDiv)
  dynamicRows.removeChild(parentDiv) // find the parent <div> of the button that was clicked and removed it
}

// from https://stackoverflow.com/a/6857116/12879037
// Find first ancestor of el with className
// or null if not found
function getParent (el, className) {
  console.log('getParent() el:', el, 'className:', className)
  while (el && el.parentNode) {
    // if the el exists and it has a parent we are assigning the parent to el
    el = el.parentNode
    console.log('getParent() el:', el, 'el.classList:', el.classList)
    if (el.classList.contains(className)) {
      return el
    }
  }
  return null
}

addRow() // adding default row

const recipeNameInput = document.getElementById('recipe-name')
console.log('recipeNameInput:', recipeNameInput)
recipeNameInput.addEventListener('input', validateRecipeName)
function validateRecipeName () {
  // if recipeNameLower is in existingSheetNames, show an error
  // otherwise, hide the error if it is already shown
  console.log('Entered recipe name')
  console.log('existingSheetNames:', existingSheetNames)
  const existingSheetNamesLower = existingSheetNames.map(item => item.toLowerCase())
  const recipeNameLower = document.form['recipe-name'].value.trim().toLowerCase()
  console.log('recipeNameLower:', recipeNameLower)
  if (existingSheetNamesLower.includes(recipeNameLower)) {
    recipeNameInput.setCustomValidity('This recipe name already exist. Please enter different name.')
  } else {
    recipeNameInput.setCustomValidity('')
    console.log('YAY!')
  }
}
/*
const ingredientNameInputs = document.getElementsByClassName('ingredient')
console.log('ingredientNameInput:', ingredientNameInputs)
for (var i = 0; i < ingredientNameInputs.length; i++) {
    ingredientNameInputs.item(i).addEventListener('input', validateIngredientName)
}
*/
// ingredientNameInput.addEventListener('input',validateIngredientName)
function validateIngredientName (event) {
  console.log('Entered ingredient name, event:', event)
  ingredientInputValue = event.target.value
  console.log('ingredientInputValue:', ingredientInputValue)
  ingredientInput = event.target // target is the object that the event happened to!!!
  console.log('ingredientInput:', ingredientInput)
  if (!validationIngredientsList.includes(ingredientInputValue)) {
    ingredientInput.setCustomValidity('Please select an ingredient from the dropdown menu. If you need to add a new ingredient refer to "Create New Ingredient" button.')
  } else {
    ingredientInput.setCustomValidity('')
    console.log('Yay!')
  }
}

// Trigers the spinner on submit
const submitButton = document.getElementById('submit-btn')
submitButton.addEventListener('click', function () {
  // form submission starts
  // button is disabled
  console.log('Clicked submit')
  const form = submitButton.form
  const isValid = form.checkValidity()
  console.log('isValid:', isValid)
  if (isValid) {
    submitButton.classList.add('loading')
    submitButton.disabled = true
    form.submit()
  }
})

function populateForm () {
  // for development only!!!
  // manually add data to the form here
  document.form['yield-qty'].value = 2000
}
// populateForm() // disable this before deploying

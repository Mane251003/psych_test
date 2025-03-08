document.addEventListener('DOMContentLoaded', function() {
    const typeSelector = document.querySelector('#id_question_type');
    const multipleChoiceField = document.querySelector('#id_multiple_choices');
    const openTextField = document.querySelector('#id_open_text_prompt');
    const ratingFields=document.querySelectorAll('#id_scale_min, #id_scale_max');
    function toggleFields() {
        const selectedType = typeSelector.value;

        if (selectedType === 'yes_no') {
            multipleChoiceField.value = JSON.stringify(['Այո', 'Ոչ']);
            multipleChoiceField.disabled = true; 
    
            openTextField.value = ''; 
            openTextField.disabled = true; 
            ratingFields.forEach(field => {
                field.value = '';
                field.disabled = true;
            });

        } else if (selectedType === 'multiple_choice') {
            multipleChoiceField.disabled = false; 
            openTextField.value = '';
            openTextField.disabled = true;
            ratingFields.forEach(field => {
                field.value = '';
                field.disabled = true;
            });   
        } else if (selectedType === 'open_text') {
            multipleChoiceField.value = '';
            multipleChoiceField.disabled = true; 
            openTextField.disabled = false; 
      
            ratingFields.forEach(field => {
                field.value = '';
                field.disabled = true;
            });
            
        } else if (selectedType === 'rating_scale'){
            multipleChoiceField.value='';
            multipleChoiceField.disabled=true;
            openTextField.value='';
            openTextField.disabled=true;
            ratingFields.forEach(field => {
                if (!field.value.trim()){
                    field.value = field.id === 'id_scale_min' ? 1 : 10;
                }
               
                field.disabled = false;
            });
        }
    }
    typeSelector.addEventListener('change', toggleFields);
    toggleFields(); 
});

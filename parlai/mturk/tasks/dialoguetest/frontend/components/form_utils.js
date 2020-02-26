import React from "react";
import _ from "lodash";

import {
  Glyphicon,
  Row,
  Col,
  FormControl,
  Button,
  ButtonGroup,
  InputGroup,
  FormGroup,
  MenuItem,
  DropdownButton,
  Badge,
  Checkbox,
  Radio,
  Popover,
  Overlay,
  Nav,
  NavItem,
  ControlLabel,
  Form,
  Tabs,
  Tab,
  HelpBlock
} from "react-bootstrap";
import * as constants from "./constants";

function FieldGroup({ id, label, help, ...props }) {
  return (
    <FormGroup controlId={id}>
      <ControlLabel>{label}</ControlLabel>
      <FormControl {...props} />
      {help && <HelpBlock>{help}</HelpBlock>}
    </FormGroup>
  );
}

function ControlLabelWithRemove(props) {
  return (
    <ControlLabel>
      {props.property}
      <Button
        style={{ border: 0, padding: "3px 6px", background: "transparent" }}
        onClick={() => props.onRemove(props.category, props.property)}
      >
        <Glyphicon glyph="remove" />
      </Button>

    </ControlLabel>
  );
}

export function jsonToForm(
  json,
  category,
  activeFormFields,
  removeFormField,
  values,
  onChangeValue
) {
  const inputByName = _.keyBy(json.input, "Name");

  return activeFormFields.map(formFieldName => {
    const input = inputByName[formFieldName];
    const isRequired = json.required.indexOf(input.Name) >= 0;
    const controlLabelWithRemove = (
      <ControlLabelWithRemove
        property={input.Name}
        name={`${constants.FIELD_VALUE_PREFIX}${input.Name}`}
        category={category}
        onRemove={removeFormField}
      />
    );
    switch (input.Type) {
      case "LongString": {
        const fieldName = `${constants.FIELD_VALUE_PREFIX}${input.Name}`;
        return (
          <FormGroup>
            {controlLabelWithRemove}
            <FormControl
              required={isRequired}
              name={fieldName}
              componentClass="textarea"
              placeholder="textarea"
              value={values[fieldName]}
              onChange={event => onChangeValue(fieldName, event.target.value)}
            />
          </FormGroup>
        );
      }
      case "ShortString": {
        const fieldName = `${constants.FIELD_VALUE_PREFIX}${input.Name}`;
        return (
          <FormGroup>
            {controlLabelWithRemove}
            <FormControl
              name={fieldName}
              required={isRequired}
              componentClass="input"
              style={{ maxWidth: 400 }}
              value={values[fieldName]}
              onChange={event => onChangeValue(fieldName, event.target.value)}
            />
          </FormGroup>
        );
      }
      case "Categorical":
      case "CategoricalMultiple": {
        const uiLogicInfo = {
          Categorical: {
            is_equal_to: "SingleSelect",
            is_one_of: "MultiSelect"
            // Todo: Probably easier if the back-end provides "is_not_equal" ?
            // is_not: "SingleSelect"
          },
          CategoricalMultiple: {
            is_equal_to: "MultiSelect",
            contains: "SingleSelect",
            contain_all_of: "MultiSelect",
            contain_at_least_one_of: "MultiSelect"
          }
        }[input.Type];

        const operatorFieldName = `${constants.FIELD_OPERATOR_PREFIX}${input.Name}`;
        const fieldName = `${constants.FIELD_VALUE_PREFIX}${input.Name}`;

        const operatorUi = (
          <FormControl
            name={operatorFieldName}
            componentClass="select"
            placeholder={Object.keys(uiLogicInfo)[0]}
            style={{ maxWidth: 130, display: "inline-block" }}
            value={values[operatorFieldName]}
            onChange={event =>
              onChangeValue(operatorFieldName, event.target.value)}
          >
            {Object.keys(uiLogicInfo).map(key =>
              <option value={key}>{key.replace(/_/g, " ")}</option>
            )}
          </FormControl>
        );

        const isMultiple =
          uiLogicInfo[values[operatorFieldName]] === "MultiSelect";

        return (
          <FormGroup>
            {controlLabelWithRemove}
            <div>
              {operatorUi}
              <FormControl
                required={isRequired}
                name={fieldName}
                componentClass="select"
                placeholder="select"
                multiple={isMultiple}
                value={values[fieldName]}
                onChange={event => {
                  if (event.target.multiple) {
                    const selectedOptions = Array.from(
                      event.target.querySelectorAll("option:checked"),
                      e => e.value
                    );
                    onChangeValue(fieldName, selectedOptions);
                  } else {
                    onChangeValue(fieldName, event.target.value);
                  }
                }}
                style={{
                  maxWidth: 200,
                  display: "inline-block",
                  verticalAlign: "top",
                  marginLeft: 10
                }}
              >
                {input.Categories.map((category, idx) =>
                  <option key={`${category}-idx`} value={category}>
                    {category}
                  </option>
                )}
              </FormControl>
            </div>
          </FormGroup>
        );
      }
      case "Boolean": {
        const fieldName = `${constants.FIELD_VALUE_PREFIX}${input.Name}`;
        return (
          <FormGroup>
            <Checkbox
              name={fieldName}
              required={isRequired}
              value={values[fieldName]}
              onChange={event => onChangeValue(fieldName, event.target.checked)}
              inline
            >
              {input.Name}
            </Checkbox>
            <Button
              style={{
                border: 0,
                padding: "3px 6px",
                background: "transparent"
              }}
              onClick={() => removeFormField(category, input.Name)}
            >
              <Glyphicon glyph="remove" />
            </Button>
          </FormGroup>
        );
      }
      case "Integer": {
        // TODO (high-pri): more operators for all data types

        const { Min, Max } = input;

        const operatorFieldName = `${constants.FIELD_OPERATOR_PREFIX}${input.Name}`;
        const fieldName = `${constants.FIELD_VALUE_PREFIX}${input.Name}`;

        return (
          <FormGroup controlId="formControlsNumber">
            {controlLabelWithRemove}
            <div>
              <FormControl
                required={isRequired}
                name={operatorFieldName}
                componentClass="select"
                placeholder="is"
                style={{ maxWidth: 130, display: "inline-block" }}
                value={values[operatorFieldName]}
                onChange={event =>
                  onChangeValue(operatorFieldName, event.target.value)}
              >
                <option value="is_equal_to">is equal to</option>
                <option value="is_greater_than">is greater than</option>
                <option value="is_less_than">is less than</option>
                <option value="is_not">is not</option>
              </FormControl>
              <FormControl
                required={isRequired}
                name={fieldName}
                componentClass="input"
                type="number"
                min={Min}
                max={Max}
                style={{
                  maxWidth: 200,
                  display: "inline-block",
                  marginLeft: 20
                }}
                value={values[fieldName]}
                onChange={event => onChangeValue(fieldName, event.target.value)}
              />
            </div>
          </FormGroup>
        );
      }
    }
  });
}

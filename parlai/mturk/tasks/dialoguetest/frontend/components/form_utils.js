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
      {props.formFieldName}
      <Button
        style={{ border: 0, padding: "3px 6px", background: "transparent" }}
        onClick={() => props.onRemove(props.category, props.formFieldId)}
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
  formFieldData,
  onChangeValue
) {
  const inputByName = _.keyBy(json.input, "Name");
  return activeFormFields.map(formFieldWithId => {
    const formFieldName = formFieldWithId.fieldName;
    const formFieldId = formFieldWithId.id;

    const input = inputByName[formFieldName];
    const isRequired = json.required.indexOf(input.Name) >= 0;
    const controlLabelWithRemove = (
      <ControlLabelWithRemove
        formFieldName={formFieldName}
        formFieldId={formFieldId}
        category={category}
        onRemove={removeFormField}
      />
    );

    const formFieldDatum = formFieldData[formFieldId] || {
      id: formFieldId,
      fieldName: formFieldName,
      value: null,
      operatorValue: null
    };

    switch (input.Type) {
      case "LongString": {
        return (
          <FormGroup>
            {controlLabelWithRemove}
            <FormControl
              required={isRequired}
              name={formFieldId}
              componentClass="textarea"
              placeholder="textarea"
              value={formFieldDatum.value}
              onChange={event =>
                onChangeValue({
                  ...formFieldDatum,
                  value: event.target.value
                })}
            />
          </FormGroup>
        );
      }
      case "ShortString": {
        // const formFieldId = `${constants.FIELD_VALUE_PREFIX}${formFieldId}`;
        return (
          <FormGroup>
            {controlLabelWithRemove}
            <FormControl
              name={formFieldId}
              required={isRequired}
              componentClass="input"
              style={{ maxWidth: 400 }}
              value={formFieldDatum.value}
              onChange={event =>
                onChangeValue({
                  ...formFieldDatum,
                  value: event.target.value
                })}
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

        const operatorformFieldId = `${constants.FIELD_OPERATOR_PREFIX}${formFieldId}`;
        // const formFieldId = `${constants.FIELD_VALUE_PREFIX}${formFieldId}`;

        const operatorUi = (
          <FormControl
            name={operatorformFieldId}
            componentClass="select"
            placeholder={Object.keys(uiLogicInfo)[0]}
            style={{ maxWidth: 130, display: "inline-block" }}
            value={formFieldDatum.operatorValue}
            onChange={event =>
              onChangeValue({
                ...formFieldDatum,
                operatorValue: event.target.value
              })}
          >
            {Object.keys(uiLogicInfo).map(key =>
              <option value={key}>{key.replace(/_/g, " ")}</option>
            )}
          </FormControl>
        );

        const isMultiple =
          uiLogicInfo[formFieldDatum.operatorValue] === "MultiSelect";

        return (
          <FormGroup>
            {controlLabelWithRemove}
            <div>
              {operatorUi}
              <FormControl
                required={isRequired}
                name={formFieldId}
                componentClass="select"
                placeholder="select"
                multiple={isMultiple}
                value={formFieldDatum.value}
                onChange={event => {
                  if (event.target.multiple) {
                    const selectedOptions = Array.from(
                      event.target.querySelectorAll("option:checked"),
                      e => e.value
                    );
                    onChangeValue({
                      ...formFieldDatum,
                      value: selectedOptions
                    });
                  } else {
                    onChangeValue({
                      ...formFieldDatum,
                      value: event.target.value
                    });
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
        // const formFieldId = `${constants.FIELD_VALUE_PREFIX}${formFieldId}`;
        return (
          <FormGroup>
            <Checkbox
              name={formFieldId}
              required={isRequired}
              value={formFieldDatum.value}
              onChange={event =>
                onChangeValue({
                  ...formFieldDatum,
                  value: event.target.checked
                })}
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
              onClick={() => removeFormField(category, formFieldId)}
            >
              <Glyphicon glyph="remove" />
            </Button>
          </FormGroup>
        );
      }
      case "Integer": {
        // TODO (high-pri): more operators for all data types

        const { Min, Max } = input;

        const operatorformFieldId = `${constants.FIELD_OPERATOR_PREFIX}${formFieldId}`;

        return (
          <FormGroup controlId="formControlsNumber">
            {controlLabelWithRemove}
            <div>
              <FormControl
                required={isRequired}
                name={operatorformFieldId}
                componentClass="select"
                placeholder="is"
                style={{ maxWidth: 180, display: "inline-block" }}
                value={formFieldDatum.operatorValue}
                onChange={event =>
                  onChangeValue({
                    ...formFieldDatum,
                    operatorValue: event.target.value
                  })}
              >
                <option value="is_equal_to">is equal to</option>
                <option value="is_greater_than">is greater than</option>
                <option value="is_less_than">is less than</option>
                <option value="is_not">is not</option>
              </FormControl>
              <FormControl
                required={isRequired}
                name={formFieldId}
                componentClass="input"
                type="number"
                min={Min}
                max={Max}
                style={{
                  maxWidth: 150,
                  display: "inline-block",
                  marginLeft: 20
                }}
                value={formFieldDatum.value}
                onChange={event =>
                  onChangeValue({
                    ...formFieldDatum,
                    value: parseFloat(event.target.value)
                  })}
              />
            </div>
          </FormGroup>
        );
      }
    }
  });
}
